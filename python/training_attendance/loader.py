from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import oracledb
from dotenv import load_dotenv

from python.training_attendance.parser import (
    parse_meeting_file,
)


PIPELINE_NAME = "TRAINING_ATTENDANCE"


def get_scalar_value(value: Any) -> Any:
    if isinstance(value, list):
        return value[0]

    return value


def get_connection() -> oracledb.Connection:
    load_dotenv()

    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")

    if not user or not password or not dsn:
        raise ValueError(
            "ORACLE_USER, ORACLE_PASSWORD and ORACLE_DSN "
            "must be configured in .env."
        )

    return oracledb.connect(
        user=user,
        password=password,
        dsn=dsn,
    )


def file_already_loaded(
    connection: oracledb.Connection,
    source_file_hash: str,
) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM sources.training_session_raw
            WHERE source_file_hash = :source_file_hash
            """,
            source_file_hash=source_file_hash,
        )

        return cursor.fetchone()[0] > 0


def start_run(
    connection: oracledb.Connection,
    source_file_name: str,
) -> int:
    with connection.cursor() as cursor:
        run_id_variable = cursor.var(oracledb.NUMBER)

        cursor.callproc(
            "etl_control.pkg_etl_audit.start_run",
            [
                PIPELINE_NAME,
                source_file_name,
                run_id_variable,
            ],
        )

        return int(
            get_scalar_value(
                run_id_variable.getvalue()
            )
        )


def finish_success(
    connection: oracledb.Connection,
    run_id: int,
    rows_read: int,
    rows_loaded: int,
) -> None:
    with connection.cursor() as cursor:
        cursor.callproc(
            "etl_control.pkg_etl_audit.finish_run_success",
            [
                run_id,
                rows_read,
                rows_loaded,
                0,
            ],
        )


def finish_failed(
    connection: oracledb.Connection,
    run_id: int,
    source_file_name: str,
    error: Exception,
) -> None:
    with connection.cursor() as cursor:
        cursor.callproc(
            "etl_control.pkg_etl_audit.log_error",
            [
                run_id,
                PIPELINE_NAME,
                source_file_name,
                None,
                type(error).__name__,
                str(error),
                source_file_name,
            ],
        )

        cursor.callproc(
            "etl_control.pkg_etl_audit.finish_run_failed",
            [
                run_id,
                0,
                0,
                0,
                str(error),
            ],
        )


def load_meeting_file(
    connection: oracledb.Connection,
    file_path: Path,
) -> None:
    parsed = parse_meeting_file(file_path)
    metadata = parsed["metadata"]
    session = parsed["session"]

    if file_already_loaded(
        connection,
        metadata["source_file_hash"],
    ):
        print(f"Skipped duplicate file: {file_path.name}")
        return

    run_id = start_run(
        connection,
        metadata["source_file_name"],
    )

    rows_read = (
        1
        + len(parsed["participants"])
        + len(parsed["activities"])
    )

    try:
        with connection.cursor() as cursor:
            session_id_variable = cursor.var(
                oracledb.NUMBER
            )

            cursor.execute(
                """
                INSERT INTO sources.training_session_raw (
                    session_source_key,
                    run_id,
                    dataset_name,
                    source_file_name,
                    source_file_hash,
                    meeting_title_raw,
                    attended_participants_raw,
                    start_time_raw,
                    end_time_raw,
                    meeting_duration_raw,
                    average_attendance_time_raw
                )
                VALUES (
                    :session_source_key,
                    :run_id,
                    :dataset_name,
                    :source_file_name,
                    :source_file_hash,
                    :meeting_title_raw,
                    :attended_participants_raw,
                    :start_time_raw,
                    :end_time_raw,
                    :meeting_duration_raw,
                    :average_attendance_time_raw
                )
                RETURNING session_raw_id
                INTO :session_raw_id
                """,
                session_source_key=session[
                    "session_source_key"
                ],
                run_id=run_id,
                dataset_name=metadata["dataset_name"],
                source_file_name=metadata[
                    "source_file_name"
                ],
                source_file_hash=metadata[
                    "source_file_hash"
                ],
                meeting_title_raw=session.get(
                    "meeting_title_raw"
                ),
                attended_participants_raw=session.get(
                    "attended_participants_raw"
                ),
                start_time_raw=session.get(
                    "start_time_raw"
                ),
                end_time_raw=session.get(
                    "end_time_raw"
                ),
                meeting_duration_raw=session.get(
                    "meeting_duration_raw"
                ),
                average_attendance_time_raw=session.get(
                    "average_attendance_time_raw"
                ),
                session_raw_id=session_id_variable,
            )

            session_raw_id = int(
                get_scalar_value(
                    session_id_variable.getvalue()
                )
            )

            participant_rows = [
                {
                    "session_raw_id": session_raw_id,
                    "run_id": run_id,
                    "dataset_name": metadata[
                        "dataset_name"
                    ],
                    "source_file_name": metadata[
                        "source_file_name"
                    ],
                    **participant,
                }
                for participant in parsed["participants"]
            ]

            if participant_rows:
                cursor.executemany(
                    """
                    INSERT INTO sources.training_participant_raw (
                        session_raw_id,
                        run_id,
                        dataset_name,
                        source_file_name,
                        source_row_number,
                        participant_name_raw,
                        first_join_raw,
                        last_leave_raw,
                        in_meeting_duration_raw,
                        email_raw,
                        participant_id_raw,
                        role_raw,
                        raw_record
                    )
                    VALUES (
                        :session_raw_id,
                        :run_id,
                        :dataset_name,
                        :source_file_name,
                        :source_row_number,
                        :participant_name_raw,
                        :first_join_raw,
                        :last_leave_raw,
                        :in_meeting_duration_raw,
                        :email_raw,
                        :participant_id_raw,
                        :role_raw,
                        :raw_record
                    )
                    """,
                    participant_rows,
                )

            activity_rows = [
                {
                    "session_raw_id": session_raw_id,
                    "run_id": run_id,
                    "dataset_name": metadata[
                        "dataset_name"
                    ],
                    "source_file_name": metadata[
                        "source_file_name"
                    ],
                    **activity,
                }
                for activity in parsed["activities"]
            ]

            if activity_rows:
                cursor.executemany(
                    """
                    INSERT INTO sources.training_activity_raw (
                        session_raw_id,
                        run_id,
                        dataset_name,
                        source_file_name,
                        source_row_number,
                        participant_name_raw,
                        join_time_raw,
                        leave_time_raw,
                        duration_raw,
                        email_raw,
                        participant_id_raw,
                        role_raw,
                        raw_record
                    )
                    VALUES (
                        :session_raw_id,
                        :run_id,
                        :dataset_name,
                        :source_file_name,
                        :source_row_number,
                        :participant_name_raw,
                        :join_time_raw,
                        :leave_time_raw,
                        :duration_raw,
                        :email_raw,
                        :participant_id_raw,
                        :role_raw,
                        :raw_record
                    )
                    """,
                    activity_rows,
                )

        connection.commit()

        finish_success(
            connection,
            run_id,
            rows_read,
            rows_read,
        )

        print(
            f"Loaded {file_path.name}: "
            f"{len(participant_rows)} participants, "
            f"{len(activity_rows)} activities, "
            f"run_id={run_id}"
        )

    except Exception as error:
        connection.rollback()

        finish_failed(
            connection,
            run_id,
            metadata["source_file_name"],
            error,
        )

        raise


def main() -> None:
    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument(
        "--input-directory",
        default="data/input",
    )

    arguments = argument_parser.parse_args()

    input_directory = Path(arguments.input_directory)

    meeting_files = sorted(
        input_directory.glob("Meeting*.csv")
    )

    if not meeting_files:
        raise FileNotFoundError(
            f"No Meeting*.csv files found in "
            f"{input_directory}."
        )

    with get_connection() as connection:
        for meeting_file in meeting_files:
            load_meeting_file(
                connection,
                meeting_file,
            )


if __name__ == "__main__":
    main()