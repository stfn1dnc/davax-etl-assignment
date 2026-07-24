from pathlib import Path

import pandas as pd

from python.exam_absences.parser import detect_format, parse_exam_absences


def write_csv(file_path: Path, rows: list[dict[str, str]]) -> None:
    pd.DataFrame(rows).to_csv(file_path, index=False)


def test_valid_matrix_format(tmp_path: Path) -> None:
    file_path = tmp_path / "Exam_Absences_matrix.csv"
    write_csv(file_path, [
        {"Name": "Alice Tache", "D_19_05_2025": "1", "D_20_05_2025": "0"},
        {"Name": "Costin Manolescu", "D_19_05_2025": "0", "D_20_05_2025": "2"},
    ])
    parsed = parse_exam_absences(file_path)
    assert parsed["metadata"]["input_format"] == "MATRIX"
    assert len(parsed["rows"]) == 2
    assert parsed["rows"][0]["source_column_name"] == "D_19_05_2025"


def test_valid_long_format(tmp_path: Path) -> None:
    file_path = tmp_path / "Exam_Absences_long.csv"
    write_csv(file_path, [
        {"Name": "Alice Tache", "Date": "2025-05-19", "ActivityCode": "1"}
    ])
    parsed = parse_exam_absences(file_path)
    assert parsed["metadata"]["input_format"] == "LONG"
    assert len(parsed["rows"]) == 1
    assert parsed["rows"][0]["activity_date_raw"] == "2025-05-19"


def test_invalid_date_is_preserved_for_staging(tmp_path: Path) -> None:
    file_path = tmp_path / "Exam_Absences_invalid_date.csv"
    write_csv(file_path, [
        {"Name": "Alice Tache", "Date": "not-a-date", "ActivityCode": "1"}
    ])
    parsed = parse_exam_absences(file_path)
    assert parsed["rows"][0]["activity_date_raw"] == "not-a-date"


def test_missing_employee_is_preserved_for_logging(tmp_path: Path) -> None:
    file_path = tmp_path / "Exam_Absences_missing_employee.csv"
    write_csv(file_path, [
        {"Name": "", "Date": "2025-05-19", "ActivityCode": "1"}
    ])
    parsed = parse_exam_absences(file_path)
    assert len(parsed["rows"]) == 1
    assert parsed["rows"][0]["employee_id_raw"] == ""


def test_unknown_code_is_preserved_for_logging(tmp_path: Path) -> None:
    file_path = tmp_path / "Exam_Absences_unknown_code.csv"
    write_csv(file_path, [
        {"Name": "Alice Tache", "Date": "2025-05-19", "ActivityCode": "X"}
    ])
    parsed = parse_exam_absences(file_path)
    assert parsed["rows"][0]["activity_code_raw"] == "X"


def test_empty_and_zero_cells_are_ignored(tmp_path: Path) -> None:
    file_path = tmp_path / "Exam_Absences_empty.csv"
    write_csv(file_path, [
        {"Name": "Alice Tache", "D_19_05_2025": "", "D_20_05_2025": "0"}
    ])
    parsed = parse_exam_absences(file_path)
    assert parsed["rows"] == []


def test_duplicate_rows_are_preserved_for_staging(tmp_path: Path) -> None:
    file_path = tmp_path / "Exam_Absences_duplicate.csv"
    write_csv(file_path, [
        {"Name": "Alice Tache", "Date": "2025-05-19", "ActivityCode": "1"},
        {"Name": "Alice Tache", "Date": "2025-05-19", "ActivityCode": "1"},
    ])
    parsed = parse_exam_absences(file_path)
    assert len(parsed["rows"]) == 2


def test_format_is_not_guessed_when_structure_is_unknown() -> None:
    dataframe = pd.DataFrame([{"Unexpected": "value"}])
    try:
        detect_format(dataframe)
    except ValueError as error:
        assert "Could not detect" in str(error)
    else:
        raise AssertionError("ValueError was not raised")
