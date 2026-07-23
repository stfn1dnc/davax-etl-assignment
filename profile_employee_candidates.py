from __future__ import annotations

from collections import Counter
from pathlib import Path
import csv
import io
import re

import pandas as pd


INPUT_DIRECTORY = Path("data/input")

SUPPORTED_ENCODINGS = (
    "utf-8-sig",
    "utf-8",
    "cp1252",
    "latin1",
)

SUPPORTED_DELIMITERS = (
    ",",
    ";",
    "\t",
    "|",
)

COLUMN_ALIASES = {
    "employee_id": (
        "employee_id",
        "employeeid",
        "employee_code",
        "employee_number",
        "emp_id",
        "resource_id",
        "worker_id",
        "person_id",
    ),
    "employee_name": (
        "employee_name",
        "employeename",
        "full_name",
        "fullname",
    ),
    "grade": (
        "grade",
        "employee_grade",
        "level",
        "seniority",
    ),
    "discipline": (
        "discipline",
        "department",
        "capability",
        "competency",
        "practice",
    ),
    "line_manager": (
        "line_manager",
        "linemanager",
        "manager",
        "manager_name",
        "manager_id",
        "manager_email",
        "supervisor",
    ),
    "delivery_unit": (
        "delivery_unit",
        "deliveryunit",
        "du",
        "business_unit",
        "businessunit",
        "unit",
    ),
}

REQUIRED_EMPLOYEE_MASTER_COLUMNS = (
    "employee_id",
    "grade",
    "discipline",
    "line_manager",
    "delivery_unit",
)

HEADER_HINTS = {
    "name",
    "employee",
    "employee_id",
    "email",
    "grade",
    "discipline",
    "manager",
    "line_manager",
    "delivery_unit",
    "project",
    "date",
    "hours",
    "duration",
    "attendance",
    "status",
    "role",
    "join",
    "leave",
    "participant",
}


def normalize_header(value: object) -> str:
    """
    Convert a source header to a comparable snake_case representation.
    """
    normalized = str(value).strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_")


def read_text(path: Path) -> tuple[str, str]:
    """
    Read a text file using the first supported encoding that succeeds.

    Returns:
        tuple containing:
        - decoded file content
        - detected encoding
    """
    raw_content = path.read_bytes()
    last_error: UnicodeDecodeError | None = None

    for encoding in SUPPORTED_ENCODINGS:
        try:
            return raw_content.decode(encoding), encoding
        except UnicodeDecodeError as exc:
            last_error = exc

    raise ValueError(
        f"Nu am putut detecta encoding-ul pentru {path.name}."
    ) from last_error


def parse_rows(
    text: str,
    delimiter: str,
) -> list[list[str]]:
    """
    Parse CSV rows using Python's csv module.

    Unlike pandas.read_csv, this allows us to inspect mixed-section CSV files
    before deciding where the actual tabular section starts.
    """
    reader = csv.reader(
        io.StringIO(text),
        delimiter=delimiter,
    )

    return list(reader)


def is_non_empty_row(row: list[str]) -> bool:
    return any(str(value).strip() != "" for value in row)


def detect_delimiter_and_table_width(
    text: str,
) -> tuple[str, int, list[list[str]]]:
    """
    Detect the most likely delimiter and dominant table width.

    Some meeting exports contain:
    - a summary section with two fields;
    - a participant table with more fields.

    The dominant repeated row width is used as the actual table layout.
    """
    candidates: list[
        tuple[tuple[int, int, int], str, int, list[list[str]]]
    ] = []

    for delimiter in SUPPORTED_DELIMITERS:
        try:
            rows = parse_rows(text, delimiter)
        except csv.Error:
            continue

        widths = [
            len(row)
            for row in rows
            if is_non_empty_row(row)
        ]

        if not widths:
            continue

        width_counts = Counter(
            width
            for width in widths
            if width > 1
        )

        if not width_counts:
            continue

        dominant_width, dominant_count = max(
            width_counts.items(),
            key=lambda item: (
                item[1],  # number of rows with this width
                item[0],  # prefer wider table when counts are equal
            ),
        )

        multi_column_rows = sum(
            1
            for width in widths
            if width > 1
        )

        score = (
            dominant_count,
            dominant_width,
            multi_column_rows,
        )

        candidates.append(
            (
                score,
                delimiter,
                dominant_width,
                rows,
            )
        )

    if not candidates:
        raise ValueError(
            "Nu am putut detecta un delimitator tabelar valid."
        )

    _, delimiter, dominant_width, rows = max(
        candidates,
        key=lambda candidate: candidate[0],
    )

    return delimiter, dominant_width, rows


def header_score(
    row: list[str],
    row_index: int,
    all_rows: list[list[str]],
    expected_width: int,
) -> tuple[int, int, int, int]:
    """
    Score a possible header row.

    A good header:
    - contains known header words;
    - is followed by rows of the same width;
    - contains textual values;
    - appears earlier in the file.
    """
    normalized_cells = [
        normalize_header(cell)
        for cell in row
    ]

    hint_hits = 0

    for normalized_cell in normalized_cells:
        cell_tokens = set(
            token
            for token in normalized_cell.split("_")
            if token
        )

        if normalized_cell in HEADER_HINTS:
            hint_hits += 1
        elif cell_tokens.intersection(HEADER_HINTS):
            hint_hits += 1

    following_same_width = 0

    for next_index in range(
        row_index + 1,
        min(row_index + 6, len(all_rows)),
    ):
        next_row = all_rows[next_index]

        if (
            is_non_empty_row(next_row)
            and len(next_row) == expected_width
        ):
            following_same_width += 1

    textual_cells = sum(
        1
        for cell in row
        if any(character.isalpha() for character in str(cell))
    )

    return (
        hint_hits,
        following_same_width,
        textual_cells,
        -row_index,
    )


def detect_header_row(
    rows: list[list[str]],
    expected_width: int,
) -> int:
    """
    Find the most likely table header among rows having the dominant width.
    """
    candidates: list[
        tuple[tuple[int, int, int, int], int]
    ] = []

    for row_index, row in enumerate(rows):
        if not is_non_empty_row(row):
            continue

        if len(row) != expected_width:
            continue

        candidates.append(
            (
                header_score(
                    row=row,
                    row_index=row_index,
                    all_rows=rows,
                    expected_width=expected_width,
                ),
                row_index,
            )
        )

    if not candidates:
        raise ValueError(
            "Nu am putut identifica randul de header."
        )

    _, header_index = max(
        candidates,
        key=lambda candidate: candidate[0],
    )

    return header_index


def make_unique_headers(
    raw_headers: list[str],
) -> list[str]:
    """
    Ensure that blank or duplicate headers can be used in a DataFrame.
    """
    unique_headers: list[str] = []
    occurrence_count: dict[str, int] = {}

    for column_number, raw_header in enumerate(
        raw_headers,
        start=1,
    ):
        clean_header = str(raw_header).strip()

        if not clean_header:
            clean_header = f"unnamed_column_{column_number}"

        occurrence_count[clean_header] = (
            occurrence_count.get(clean_header, 0) + 1
        )

        occurrence = occurrence_count[clean_header]

        if occurrence > 1:
            clean_header = f"{clean_header}_{occurrence}"

        unique_headers.append(clean_header)

    return unique_headers


def read_mixed_csv(
    path: Path,
) -> pd.DataFrame:
    """
    Read the dominant tabular section from a potentially mixed-section CSV.
    """
    text, encoding = read_text(path)

    delimiter, table_width, rows = (
        detect_delimiter_and_table_width(text)
    )

    header_index = detect_header_row(
        rows=rows,
        expected_width=table_width,
    )

    headers = make_unique_headers(
        rows[header_index]
    )

    data_rows: list[list[str]] = []
    skipped_non_matching_rows = 0

    for row in rows[header_index + 1 :]:
        if not is_non_empty_row(row):
            continue

        if len(row) != table_width:
            skipped_non_matching_rows += 1
            continue

        data_rows.append(row)

    dataframe = pd.DataFrame(
        data_rows,
        columns=headers,
    )

    dataframe.attrs["encoding"] = encoding
    dataframe.attrs["delimiter"] = delimiter
    dataframe.attrs["header_row_number"] = header_index + 1
    dataframe.attrs["table_width"] = table_width
    dataframe.attrs["skipped_non_matching_rows"] = (
        skipped_non_matching_rows
    )

    return dataframe


def resolve_employee_columns(
    columns: list[str],
) -> dict[str, str | None]:
    normalized_to_original: dict[str, str] = {}

    for original_column in columns:
        normalized_column = normalize_header(
            original_column
        )

        normalized_to_original[normalized_column] = (
            original_column
        )

    resolved: dict[str, str | None] = {}

    for canonical_name, aliases in COLUMN_ALIASES.items():
        resolved[canonical_name] = next(
            (
                normalized_to_original[alias]
                for alias in aliases
                if alias in normalized_to_original
            ),
            None,
        )

    return resolved


def main() -> None:
    csv_files = sorted(
        INPUT_DIRECTORY.glob("*.csv")
    )

    if not csv_files:
        raise SystemExit(
            "Nu exista fisiere CSV in data/input."
        )

    employee_master_candidates: list[str] = []

    for path in csv_files:
        print("=" * 80)
        print(f"Fisier: {path.name}")

        try:
            dataframe = read_mixed_csv(path)
        except Exception as exc:
            print(
                "STATUS: EROARE DE CITIRE"
            )
            print(
                f"Tip eroare: {type(exc).__name__}"
            )
            print(
                f"Mesaj: {exc}"
            )

            # Continue profiling the remaining files.
            continue

        resolved_columns = resolve_employee_columns(
            [str(column) for column in dataframe.columns]
        )

        print(
            f"Encoding detectat: "
            f"{dataframe.attrs['encoding']}"
        )
        print(
            f"Delimiter detectat: "
            f"{repr(dataframe.attrs['delimiter'])}"
        )
        print(
            f"Header detectat la randul fizic: "
            f"{dataframe.attrs['header_row_number']}"
        )
        print(
            f"Latime tabel detectata: "
            f"{dataframe.attrs['table_width']} coloane"
        )
        print(
            f"Randuri tabelare: {len(dataframe)}"
        )
        print(
            "Randuri non-tabelare ignorate dupa header: "
            f"{dataframe.attrs['skipped_non_matching_rows']}"
        )
        print(
            f"Coloane: {list(dataframe.columns)}"
        )

        print("Coloane Employee identificate:")

        for canonical_name, source_name in (
            resolved_columns.items()
        ):
            print(
                f"  {canonical_name}: {source_name}"
            )

        all_required_found = all(
            resolved_columns[column_name] is not None
            for column_name
            in REQUIRED_EMPLOYEE_MASTER_COLUMNS
        )

        print(
            "Candidat Employee Master complet: "
            f"{all_required_found}"
        )

        if all_required_found:
            employee_master_candidates.append(
                path.name
            )

    print("=" * 80)
    print("REZUMAT EMPLOYEE MASTER DATA")

    if employee_master_candidates:
        print(
            "Fisiere candidate:"
        )

        for candidate in employee_master_candidates:
            print(
                f"  - {candidate}"
            )
    else:
        print(
            "Niciun fisier nu contine toate atributele "
            "obligatorii Employee Master Data:"
        )
        print(
            "employee_id, grade, discipline, "
            "line_manager, delivery_unit"
        )


if __name__ == "__main__":
    main()