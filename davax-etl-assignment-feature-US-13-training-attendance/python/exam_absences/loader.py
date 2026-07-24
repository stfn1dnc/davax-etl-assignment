from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import oracledb

from python.common.config import get_config
from python.common.db_connection import get_connection
from python.exam_absences.parser import parse_exam_absences


PIPELINE_NAME = "EXAM_ABSENCES"


def get_scalar_value(value: Any) -> Any:
    if isinstance(value, list):
        return value[0]
    return value


def file_already_loaded(connection: oracledb.Connection, source_file_hash: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM sources.exam_absence_raw
            WHERE source_file_hash = :source_file_hash
            """,
            source_file_hash=source_file_hash,
        )
        return cursor.fetchone()[0] > 0


def start_run(connection: oracledb.Connection, source_file_name: str) -> int:
    with connection.cursor() as cursor:
        run_id_variable = cursor.var(oracledb.NUMBER)
        cursor.callproc(
            "etl_control.pkg_etl_audit.start_run",
            [PIPELINE_NAME, source_file_name, run_id_variable],
        )
        return int(get_scalar_value(run_id_variable.getvalue()))


def finish_success(
    connection: oracledb.Connection,
    run_id: int,
    rows_read: int,
    rows_loaded: int,
    rows_rejected: int,
) -> None:
    with connection.cursor() as cursor:
        cursor.callproc(
            "etl_control.pkg_etl_audit.finish_run_success",
            [run_id, rows_read, rows_loaded, rows_rejected],
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
            [run_id, 0, 0, 0, str(error)],
        )


def insert_raw_rows(
    connection: oracledb.Connection,
    run_id: int,
    parsed_file: dict[str, Any],
) -> None:
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

    if not rows_to_insert:
        return

    with connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO sources.exam_absence_raw (
                run_id,
                dataset_name,
                employee_id_raw,
                activity_date_raw,
                activity_code_raw,
                source_file_name,
                source_file_hash,
                source_row_number,
                source_column_name,
                raw_record
            )
            VALUES (
                :run_id,
                :dataset_name,
                :employee_id_raw,
                :activity_date_raw,
                :activity_code_raw,
                :source_file_name,
                :source_file_hash,
                :source_row_number,
                :source_column_name,
                :raw_record
            )
            """,
            rows_to_insert,
        )


def run_staging(connection: oracledb.Connection, run_id: int) -> None:
    with connection.cursor() as cursor:
        cursor.callproc("staging.pkg_exam_absence_stage.load_staging", [run_id])
        cursor.callproc("staging.pkg_exam_absence_stage.validate_staging", [run_id])


def count_staging_rows(connection: oracledb.Connection, run_id: int) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM staging.stg_exam_absence
            WHERE run_id = :run_id
            """,
            run_id=run_id,
        )
        return int(cursor.fetchone()[0])


def load_exam_absence_file(connection: oracledb.Connection, file_path: Path) -> None:
    parsed_file = parse_exam_absences(file_path)
    metadata = parsed_file["metadata"]

    if file_already_loaded(connection, metadata["source_file_hash"]):
        print(f"Skipped duplicate file: {file_path.name}")
        return

    run_id = start_run(connection, metadata["source_file_name"])
    rows_read = len(parsed_file["rows"])

    try:
        insert_raw_rows(connection, run_id, parsed_file)
        run_staging(connection, run_id)
        rows_loaded = count_staging_rows(connection, run_id)
        rows_rejected = rows_read - rows_loaded
        finish_success(connection, run_id, rows_read, rows_loaded, rows_rejected)

        print(
            f"Loaded {file_path.name}: "
            f"format={metadata['input_format']}, "
            f"raw_rows={rows_read}, "
            f"staging_rows={rows_loaded}, "
            f"rejected={rows_rejected}, "
            f"run_id={run_id}"
        )
    except Exception as error:
        connection.rollback()
        finish_failed(connection, run_id, metadata["source_file_name"], error)
        raise


def main() -> None:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input-directory", default="data/input")
    arguments = argument_parser.parse_args()

    input_directory = Path(arguments.input_directory)
    input_files = sorted(input_directory.glob("Exam_Absences*.csv"))
    if not input_files:
        raise FileNotFoundError(
            f"No Exam_Absences*.csv file found in {input_directory}."
        )

    config = get_config(require_database_credentials=True)
    with get_connection(config.database) as connection:
        for input_file in input_files:
            load_exam_absence_file(connection, input_file)


if __name__ == "__main__":
    main()
