from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import oracledb

from python.common.config import get_config
from python.common.db_connection import get_connection
from python.timesheet_absences.parser import (
    read_timesheet_absences,
)


PIPELINE_NAME = "TIMESHEET_ABSENCES"


def get_scalar_value(value: Any) -> Any:
    """Return the scalar value produced by an Oracle OUT parameter"""
    if isinstance(value, list):
        return value[0]

    return value


def file_already_loaded(
    connection: oracledb.Connection,
    source_file_hash: str,
) -> bool:
    """Check whether the same physical file was loaded before"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM sources.timesheet_absence_raw
            WHERE source_file_hash = :source_file_hash
            """,
            source_file_hash=source_file_hash,
        )

        return cursor.fetchone()[0] > 0


def start_run(
    connection: oracledb.Connection,
    source_file_name: str,
) -> int:
    """Create an ETL_RUN record and return its run_id"""
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
            get_scalar_value(run_id_variable.getvalue())
        )


def finish_success(
    connection: oracledb.Connection,
    run_id: int,
    rows_read: int,
    rows_loaded: int,
    rows_rejected: int,
) -> None:
    """Mark an ETL run as successful"""
    with connection.cursor() as cursor:
        cursor.callproc(
            "etl_control.pkg_etl_audit.finish_run_success",
            [
                run_id,
                rows_read,
                rows_loaded,
                rows_rejected,
            ],
        )


def finish_failed(
    connection: oracledb.Connection,
    run_id: int,
    source_file_name: str,
    error: Exception,
) -> None:
    """Write the failure to the common ETL audit tables"""
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


def insert_raw_rows(
    connection: oracledb.Connection,
    run_id: int,
    parsed_file: dict[str, Any],
) -> None:
    """Insert all parsed CSV rows into the SOURCES raw table"""
    metadata = parsed_file["metadata"]

    rows_to_insert = [
        {
            "run_id": run_id,
            "dataset_name": metadata["dataset_name"],
            "source_file_name": metadata["source_file_name"],
            "source_file_hash": metadata["source_file_hash"],
            **row,
        }
        for row in parsed_file["rows"]
    ]

    with connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO sources.timesheet_absence_raw (
                run_id,
                dataset_name,
                source_file_name,
                source_file_hash,
                source_row_number,
                name_raw,
                email_raw,
                date_worked_raw,
                absence_hours_raw,
                project_code_raw,
                raw_record
            )
            VALUES (
                :run_id,
                :dataset_name,
                :source_file_name,
                :source_file_hash,
                :source_row_number,
                :employee_name_raw,
                :employee_email_raw,
                :date_worked_raw,
                :absence_hours_raw,
                :project_code_raw,
                :raw_record
            )
            """,
            rows_to_insert,
        )


def run_staging(
    connection: oracledb.Connection,
    run_id: int,
) -> None:
    """Call the PL/SQL procedures that load and validate staging"""
    with connection.cursor() as cursor:
        cursor.callproc(
            "staging.pkg_timesheet_absence_stage.load_staging",
            [run_id],
        )

        cursor.callproc(
            "staging.pkg_timesheet_absence_stage.validate_staging",
            [run_id],
        )


def get_staging_counts(
    connection: oracledb.Connection,
    run_id: int,
) -> tuple[int, int]:
    """Return the number of valid and invalid staging rows."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                SUM(
                    CASE
                        WHEN validation_status = 'VALID' THEN 1
                        ELSE 0
                    END
                ) AS valid_rows,
                SUM(
                    CASE
                        WHEN validation_status = 'INVALID' THEN 1
                        ELSE 0
                    END
                ) AS invalid_rows
            FROM staging.stg_timesheet_absence
            WHERE run_id = :run_id
            """,
            run_id=run_id,
        )

        valid_rows, invalid_rows = cursor.fetchone()

        return int(valid_rows or 0), int(invalid_rows or 0)


def load_timesheet_absence_file(
    connection: oracledb.Connection,
    file_path: Path,
) -> None:
    """Execute the complete US-10 flow for one CSV file"""
    parsed_file = read_timesheet_absences(file_path)
    metadata = parsed_file["metadata"]

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

    rows_read = len(parsed_file["rows"])

    try:
        insert_raw_rows(
            connection,
            run_id,
            parsed_file,
        )

        run_staging(connection, run_id)

        valid_rows, invalid_rows = get_staging_counts(
            connection,
            run_id,
        )

        connection.commit()

        finish_success(
            connection,
            run_id,
            rows_read,
            valid_rows,
            invalid_rows,
        )

        print(
            f"Loaded {file_path.name}: "
            f"rows_read={rows_read}, "
            f"valid={valid_rows}, "
            f"invalid={invalid_rows}, "
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
        default=None,
    )
    arguments = argument_parser.parse_args()

    config = get_config(require_database_credentials=True)

    input_directory = (
        Path(arguments.input_directory)
        if arguments.input_directory
        else config.input_data_path
    )

    input_files = sorted(
        input_directory.glob("Timesheet_Absences*.csv")
    )

    if not input_files:
        raise FileNotFoundError(
            "No Timesheet_Absences*.csv file was found in "
            f"{input_directory}."
        )

    with get_connection(config.database) as connection:
        for input_file in input_files:
            load_timesheet_absence_file(
                connection,
                input_file,
            )


if __name__ == "__main__":
    main()
