from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = [
    "Name",
    "Email",
    "DateWorked",
    "AbsenceHours",
    "ProjectCode",
]

DATASET_NAME = "TIMESHEET_ABSENCES"


def calculate_file_hash(file_path: Path) -> str:
    """Calculate a SHA-256 hash used to identify the input file"""
    file_hash = hashlib.sha256()

    with file_path.open("rb") as input_file:
        for block in iter(lambda: input_file.read(65536), b""):
            file_hash.update(block)

    return file_hash.hexdigest()


def read_timesheet_absences(file_name: str | Path) -> dict[str, Any]:
    """Read and validate the structure of a Timesheet Absences CSV file"""
    file_path = Path(file_name)

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    if file_path.stat().st_size == 0:
        raise ValueError(f"File is empty: {file_path}")


    dataframe = pd.read_csv(
        file_path,
        dtype=str,
        keep_default_na=False,
    )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    if dataframe.empty:
        raise ValueError(
            f"File contains no data rows: {file_path}"
        )

    raw_rows: list[dict[str, Any]] = []

    for dataframe_index, row in dataframe.iterrows():
        source_values = {
            column: str(row[column]).strip()
            for column in REQUIRED_COLUMNS
        }

        raw_rows.append(
            {
                
                "source_row_number": int(dataframe_index) + 2,
                "employee_name_raw": source_values["Name"],
                "employee_email_raw": source_values["Email"],
                "date_worked_raw": source_values["DateWorked"],
                "absence_hours_raw": source_values["AbsenceHours"],
                "project_code_raw": source_values["ProjectCode"],
                "raw_record": json.dumps(
                    source_values,
                    ensure_ascii=False,
                ),
            }
        )

    return {
        "metadata": {
            "dataset_name": DATASET_NAME,
            "source_file_name": file_path.name,
            "source_file_hash": calculate_file_hash(file_path),
        },
        "rows": raw_rows,
    }


def main() -> None:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("file_path")
    arguments = argument_parser.parse_args()

    result = read_timesheet_absences(arguments.file_path)

    print(f"File: {result['metadata']['source_file_name']}")
    print(f"Dataset: {result['metadata']['dataset_name']}")
    print(f"Rows: {len(result['rows'])}")
    print(
        "File hash: "
        f"{result['metadata']['source_file_hash']}"
    )


if __name__ == "__main__":
    main()
