from pathlib import Path

import pandas as pd




MEETING_FILES = [
    "Meeting1 1.csv",
    "Meeting2 1.csv",
    "Meeting3 1.csv",
]

TIMESHEET_FILES = [
    "Timesheet__WorkedHours 1.csv",
    "Timesheet_Absences 1.csv",
]


def normalize_email(email: str) -> str:

    if pd.isna(email):
        return ""

    return str(email).strip().lower()


def normalize_name(name: str) -> str:

    if pd.isna(name):
        return ""

    return str(name).strip()

def read_csv_safely(file_path: Path) -> pd.DataFrame:

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1",
    ]

    for encoding in encodings:
        try:
            return pd.read_csv(
                file_path,
                encoding=encoding,
            )
        except UnicodeDecodeError:
            pass

    raise ValueError(
        f"Cannot read file {file_path}"
    )

def build_employee_master(
    input_directory: Path,
) -> pd.DataFrame:

    employees = []

    datasets = (
        MEETING_FILES
        + TIMESHEET_FILES
    )

    for dataset in datasets:

        if dataset.startswith("Meeting"):

             dataframe = pd.read_csv(
                input_directory / dataset,
                encoding="cp1252",
                skiprows=9,
            )

        else:

            dataframe = read_csv_safely(
                input_directory / dataset
            )

        for _, row in dataframe.iterrows():

            employees.append(
                {
                    "employee_id": normalize_email(
                        row["Email"]
                    ),
                    "employee_name": normalize_name(
                        row["Name"]
                    ),
                }
            )

    employee_master = pd.DataFrame(
        employees
    )

    employee_master = (
        employee_master
        .drop_duplicates(
            subset="employee_id"
        )
        .sort_values(
            by="employee_name"
        )
        .reset_index(drop=True)
    )

    return employee_master