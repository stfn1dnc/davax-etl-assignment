import pathlib

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


def build_employee_master():

    employees = []

    # Read meeting files
    for dataset in MEETING_FILES:

        file_path = pathlib.Path("data/input") / dataset

        dataframe = pd.read_csv(
            file_path,
            encoding="utf-16",
            sep="\t",
            skiprows=9,
        )

        dataframe = dataframe[
            [
                "Name",
                "Email",
            ]
        ]

        employees.append(dataframe)

    # Read timesheet files
    for dataset in TIMESHEET_FILES:

        file_path = pathlib.Path("data/input") / dataset

        dataframe = pd.read_csv(
            file_path,
            encoding="cp1252",
        )

        dataframe = dataframe[
            [
                "Name",
                "Email",
            ]
        ]

        employees.append(dataframe)

    employee_master = pd.concat(
        employees,
        ignore_index=True,
    )

    employee_master.columns = [
        "employee_name",
        "employee_id",
    ]

    employee_master["employee_name"] = (
        employee_master["employee_name"]
        .astype(str)
        .str.strip()
    )

    employee_master["employee_id"] = (
        employee_master["employee_id"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    employee_master = employee_master.dropna(
        subset=[
            "employee_name",
            "employee_id",
        ]
    )

    employee_master = employee_master.drop_duplicates(
        subset="employee_id"
    )

    employee_master = employee_master.sort_values(
        "employee_name"
    ).reset_index(
        drop=True
    )

    employee_master["grade"] = "JUNIOR"

    employee_master["discipline"] = "DATA_ENGINEERING"

    employee_master["line_manager"] = "UNKNOWN"

    employee_master["delivery_unit"] = "DU_DATA"

    output_folder = pathlib.Path("data/generated")

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    employee_master.to_csv(
        output_folder / "employee_master.csv",
        index=False,
    )

    return employee_master