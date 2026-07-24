from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


DATASET_NAME = "EXAM_ABSENCES"
MATRIX_DATE_PATTERN = re.compile(r"^D_\d{2}_\d{2}_\d{4}$", re.IGNORECASE)

EMPLOYEE_COLUMN_NAMES = {"name", "employee", "employeeid", "employeeidraw"}
DATE_COLUMN_NAMES = {"date", "activitydate", "activitydateraw"}
CODE_COLUMN_NAMES = {"code", "activitycode", "activitycoderaw", "absencecode"}


def normalize_column_name(value: str) -> str:
    cleaned = value.replace("\ufeff", "").strip().casefold()
    return re.sub(r"[^a-z0-9]+", "", cleaned)


def calculate_file_hash(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as input_file:
        for block in iter(lambda: input_file.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def find_column(columns: list[str], accepted_names: set[str]) -> str | None:
    for column in columns:
        if normalize_column_name(column) in accepted_names:
            return column
    return None


def detect_format(dataframe: pd.DataFrame) -> str:
    """Return LONG or MATRIX based on the available columns."""
    columns = [str(column) for column in dataframe.columns]
    employee_column = find_column(columns, EMPLOYEE_COLUMN_NAMES)
    date_column = find_column(columns, DATE_COLUMN_NAMES)
    code_column = find_column(columns, CODE_COLUMN_NAMES)

    if employee_column and date_column and code_column:
        return "LONG"

    matrix_date_columns = [
        column
        for column in columns
        if MATRIX_DATE_PATTERN.fullmatch(column.strip())
    ]

    if employee_column and matrix_date_columns:
        return "MATRIX"

    raise ValueError(
        "Could not detect Exam Absences format. "
        "Expected either a long file with employee/date/code columns "
        "or a matrix file with Name and D_DD_MM_YYYY columns."
    )


def read_exam_file(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    if file_path.stat().st_size == 0:
        raise ValueError(f"The input file is empty: {file_path.name}")

    dataframe = pd.read_csv(
        file_path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )
    if dataframe.empty:
        raise ValueError(f"The input file has no data rows: {file_path.name}")

    dataframe.columns = [
        str(column).replace("\ufeff", "").strip()
        for column in dataframe.columns
    ]
    return dataframe


def normalize_matrix(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    columns = [str(column) for column in dataframe.columns]
    employee_column = find_column(columns, EMPLOYEE_COLUMN_NAMES)
    if employee_column is None:
        raise ValueError("Employee column is missing from matrix input.")

    date_columns = [
        column
        for column in columns
        if MATRIX_DATE_PATTERN.fullmatch(column.strip())
    ]
    if not date_columns:
        raise ValueError("No matrix date columns were found.")

    working_dataframe = dataframe.copy()
    working_dataframe["_source_row_number"] = working_dataframe.index + 2

    melted = working_dataframe.melt(
        id_vars=[employee_column, "_source_row_number"],
        value_vars=date_columns,
        var_name="source_column_name",
        value_name="activity_code_raw",
    )

    normalized_rows: list[dict[str, Any]] = []
    for _, row in melted.iterrows():
        activity_code = str(row["activity_code_raw"]).strip()
        if activity_code in {"", "0"}:
            continue

        employee_value = str(row[employee_column]).strip()
        source_column_name = str(row["source_column_name"]).strip()
        normalized_rows.append(
            {
                "employee_id_raw": employee_value,
                "activity_date_raw": source_column_name,
                "activity_code_raw": activity_code,
                "source_row_number": int(row["_source_row_number"]),
                "source_column_name": source_column_name,
                "raw_record": json.dumps(
                    {
                        "employee": employee_value,
                        "date_column": source_column_name,
                        "activity_code": activity_code,
                    },
                    ensure_ascii=False,
                ),
            }
        )
    return normalized_rows


def normalize_long(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    columns = [str(column) for column in dataframe.columns]
    employee_column = find_column(columns, EMPLOYEE_COLUMN_NAMES)
    date_column = find_column(columns, DATE_COLUMN_NAMES)
    code_column = find_column(columns, CODE_COLUMN_NAMES)

    if not employee_column or not date_column or not code_column:
        raise ValueError("Long input must contain employee, date and activity code columns.")

    normalized_rows: list[dict[str, Any]] = []
    for dataframe_index, row in dataframe.iterrows():
        activity_code = str(row[code_column]).strip()
        if activity_code in {"", "0"}:
            continue

        employee_value = str(row[employee_column]).strip()
        date_value = str(row[date_column]).strip()
        normalized_rows.append(
            {
                "employee_id_raw": employee_value,
                "activity_date_raw": date_value,
                "activity_code_raw": activity_code,
                "source_row_number": int(dataframe_index) + 2,
                "source_column_name": code_column,
                "raw_record": json.dumps(
                    {
                        "employee": employee_value,
                        "activity_date": date_value,
                        "activity_code": activity_code,
                    },
                    ensure_ascii=False,
                ),
            }
        )
    return normalized_rows


def parse_exam_absences(file_path: Path) -> dict[str, Any]:
    dataframe = read_exam_file(file_path)
    input_format = detect_format(dataframe)
    rows = normalize_matrix(dataframe) if input_format == "MATRIX" else normalize_long(dataframe)

    return {
        "metadata": {
            "dataset_name": DATASET_NAME,
            "source_file_name": file_path.name,
            "source_file_hash": calculate_file_hash(file_path),
            "input_format": input_format,
            "source_row_count": len(dataframe),
            "canonical_row_count": len(rows),
        },
        "rows": rows,
    }


def main() -> None:
    import argparse
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("file_path")
    arguments = argument_parser.parse_args()

    parsed = parse_exam_absences(Path(arguments.file_path))
    metadata = parsed["metadata"]
    print(f"File: {metadata['source_file_name']}")
    print(f"Detected format: {metadata['input_format']}")
    print(f"Source rows: {metadata['source_row_count']}")
    print(f"Canonical activity rows: {metadata['canonical_row_count']}")
    print(f"File hash: {metadata['source_file_hash']}")


if __name__ == "__main__":
    main()
