import pytest

from python.timesheet_absences.parser import (
    read_timesheet_absences,
)


VALID_HEADER = (
    "Name,Email,DateWorked,AbsenceHours,ProjectCode\n"
)


def test_valid_file_is_read(tmp_path):
    input_file = tmp_path / "Timesheet_Absences 1.csv"
    input_file.write_text(
        VALID_HEADER
        + "Employee One,employee.one@example.com,24-Jun-25,2.50,PRJ101\n"
        + "Employee Two,employee.two@example.com,25-Jun-25,1.25,PRJ102\n",
        encoding="utf-8",
    )

    result = read_timesheet_absences(input_file)

    assert result["metadata"]["dataset_name"] == "TIMESHEET_ABSENCES"
    assert len(result["rows"]) == 2
    assert result["rows"][0]["source_row_number"] == 2
    assert result["rows"][0]["employee_email_raw"] == "employee.one@example.com"
    assert result["rows"][0]["absence_hours_raw"] == "2.50"


def test_missing_column_is_rejected(tmp_path):
    input_file = tmp_path / "Timesheet_Absences 1.csv"
    input_file.write_text(
        "Name,Email,DateWorked,AbsenceHours\n"
        "Employee One,employee.one@example.com,24-Jun-25,2.50\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="ProjectCode"):
        read_timesheet_absences(input_file)


def test_empty_file_is_rejected(tmp_path):
    input_file = tmp_path / "Timesheet_Absences 1.csv"
    input_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        read_timesheet_absences(input_file)


def test_invalid_source_values_are_kept_for_staging(tmp_path):
    input_file = tmp_path / "Timesheet_Absences 1.csv"
    input_file.write_text(
        VALID_HEADER
        + "Employee One,,not-a-date,not-a-number,PRJ101\n",
        encoding="utf-8",
    )

    result = read_timesheet_absences(input_file)
    first_row = result["rows"][0]

    assert first_row["employee_email_raw"] == ""
    assert first_row["date_worked_raw"] == "not-a-date"
    assert first_row["absence_hours_raw"] == "not-a-number"
