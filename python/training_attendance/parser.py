from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SUMMARY_MAPPING = {
    "meeting title": "meeting_title_raw",
    "attended participants": "attended_participants_raw",
    "start time": "start_time_raw",
    "end time": "end_time_raw",
    "meeting duration": "meeting_duration_raw",
    "average attendance time": "average_attendance_time_raw",
}

PARTICIPANT_MAPPING = {
    "name": "participant_name_raw",
    "first join": "first_join_raw",
    "last leave": "last_leave_raw",
    "in meeting duration": "in_meeting_duration_raw",
    "email": "email_raw",
    "participant id": "participant_id_raw",
    "participant id upn": "participant_id_raw",
    "role": "role_raw",
}

ACTIVITY_MAPPING = {
    "name": "participant_name_raw",
    "participant name": "participant_name_raw",
    "first join": "join_time_raw",
    "join time": "join_time_raw",
    "last leave": "leave_time_raw",
    "leave time": "leave_time_raw",
    "in meeting duration": "duration_raw",
    "duration": "duration_raw",
    "email": "email_raw",
    "participant id": "participant_id_raw",
    "participant id upn": "participant_id_raw",
    "role": "role_raw",
}


def normalize_label(value: str) -> str:
    """Normalize CSV labels for comparison."""
    normalized = (
        value
        .replace("\ufeff", "")
        .replace("\x00", "")
        .strip()
        .casefold()
    )

    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()

def calculate_file_hash(file_path: Path) -> str:
    digest = hashlib.sha256()

    with file_path.open("rb") as input_file:
        for block in iter(lambda: input_file.read(65536), b""):
            digest.update(block)

    return digest.hexdigest()


def read_csv_rows(
    file_path: Path,
) -> tuple[list[list[str]], str, str]:
    for encoding in ("utf-8-sig", "utf-8", "utf-16", "cp1252"):
        try:
            text = file_path.read_text(encoding=encoding)

            sample = text[:10000]

            if "\t" in sample:
                delimiter = "\t"
            else:
                try:
                    delimiter = csv.Sniffer().sniff(
                        sample,
                        delimiters=";|,",
                    ).delimiter
                except csv.Error:
                    delimiter = ","

            with file_path.open(
                "r",
                encoding=encoding,
                newline="",
            ) as input_file:
                rows = list(
                    csv.reader(
                        input_file,
                        delimiter=delimiter,
                    )
                )

            return rows, encoding, delimiter

        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"Could not determine encoding for {file_path}."
    )


def find_section(
    rows: list[list[str]],
    section_name: str,
) -> int:
    expected = normalize_label(section_name)

    for index, row in enumerate(rows):
        for value in row:
            current_value = normalize_label(value)

            if (
                current_value == expected
                or current_value.startswith(expected)
            ):
                return index

    preview = []

    for index, row in enumerate(rows[:30]):
        non_empty_values = [
            value
            for value in row
            if value.strip()
        ]

        if non_empty_values:
            preview.append(
                f"Row {index + 1}: {non_empty_values!r}"
            )

    raise ValueError(
        f"Section not found: {section_name}\n"
        "First non-empty CSV rows:\n"
        + "\n".join(preview)
    )

def parse_summary(
    rows: list[list[str]],
    start_index: int,
    end_index: int,
) -> dict[str, str]:
    summary: dict[str, str] = {}

    for row in rows[start_index + 1 : end_index]:
        if len(row) < 2:
            continue

        field_name = SUMMARY_MAPPING.get(
            normalize_label(row[0])
        )

        if field_name:
            summary[field_name] = row[1].strip()

    required_fields = {
        "meeting_title_raw",
        "start_time_raw",
        "end_time_raw",
    }

    missing_fields = required_fields - summary.keys()

    if missing_fields:
        raise ValueError(
            "Missing summary fields: "
            + ", ".join(sorted(missing_fields))
        )

    return summary


def find_table_header(
    rows: list[list[str]],
    start_index: int,
    end_index: int,
    mapping: dict[str, str],
) -> tuple[int, list[str | None]]:
    best_header_index: int | None = None
    best_mapping: list[str | None] = []
    best_score = 0

    for index in range(start_index + 1, end_index):
        mapped_columns = [
            mapping.get(normalize_label(value))
            for value in rows[index]
        ]

        score = sum(
            field_name is not None
            for field_name in mapped_columns
        )

        if score > best_score:
            best_score = score
            best_header_index = index
            best_mapping = mapped_columns

        if score >= 4:
            break

    if best_header_index is None or best_score < 2:
        raise ValueError(
            f"Could not find table header after CSV row "
            f"{start_index + 1}."
        )

    return best_header_index, best_mapping


def parse_table(
    rows: list[list[str]],
    start_index: int,
    end_index: int,
    mapping: dict[str, str],
) -> list[dict[str, Any]]:
    header_index, mapped_columns = find_table_header(
        rows,
        start_index,
        end_index,
        mapping,
    )

    known_fields = set(mapping.values())
    parsed_rows: list[dict[str, Any]] = []

    for row_index in range(header_index + 1, end_index):
        row = rows[row_index]

        if not any(value.strip() for value in row):
            continue

        record: dict[str, Any] = {
            field_name: ""
            for field_name in known_fields
        }

        record["source_row_number"] = row_index + 1
        record["raw_record"] = json.dumps(
            row,
            ensure_ascii=False,
        )

        for column_index, field_name in enumerate(
            mapped_columns
        ):
            if field_name is None:
                continue

            record[field_name] = (
                row[column_index].strip()
                if column_index < len(row)
                else ""
            )

        has_participant_identity = any(
            record.get(field_name)
            for field_name in (
                "participant_name_raw",
                "email_raw",
                "participant_id_raw",
            )
        )

        if has_participant_identity:
            parsed_rows.append(record)

    return parsed_rows


def parse_meeting_file(
    file_name: str | Path,
) -> dict[str, Any]:
    file_path = Path(file_name)

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    if file_path.stat().st_size == 0:
        raise ValueError(f"File is empty: {file_path}")

    rows, encoding, delimiter = read_csv_rows(file_path)

    summary_index = find_section(rows, "1. Summary")
    participant_index = find_section(rows, "2. Participants")
    activity_index = find_section(
        rows,
        "3. In-Meeting Activities",
    )

    if not (
        summary_index
        < participant_index
        < activity_index
    ):
        raise ValueError(
            "The meeting sections are not in the expected order."
        )

    summary = parse_summary(
        rows,
        summary_index,
        participant_index,
    )

    participants = parse_table(
        rows,
        participant_index,
        activity_index,
        PARTICIPANT_MAPPING,
    )

    activities = parse_table(
        rows,
        activity_index,
        len(rows),
        ACTIVITY_MAPPING,
    )

    source_file_hash = calculate_file_hash(file_path)

    session_natural_key = "|".join(
        (
            summary["meeting_title_raw"].strip().casefold(),
            summary["start_time_raw"].strip(),
        )
    )

    session_source_key = hashlib.sha256(
        session_natural_key.encode("utf-8")
    ).hexdigest()

    return {
        "metadata": {
            "dataset_name": "TRAINING_ATTENDANCE",
            "source_file_name": file_path.name,
            "source_file_hash": source_file_hash,
            "encoding": encoding,
            "delimiter": delimiter,
        },
        "session": {
            "session_source_key": session_source_key,
            **summary,
        },
        "participants": participants,
        "activities": activities,
    }


def main() -> None:
    import argparse

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("file_name")
    arguments = argument_parser.parse_args()

    result = parse_meeting_file(arguments.file_name)

    print(f"File: {result['metadata']['source_file_name']}")
    print(f"Encoding: {result['metadata']['encoding']}")
    print(f"Delimiter: {result['metadata']['delimiter']!r}")
    print(f"Meeting: {result['session']['meeting_title_raw']}")
    print(
        "Reported participants: "
        f"{result['session'].get('attended_participants_raw')}"
    )
    print(f"Parsed participants: {len(result['participants'])}")
    print(f"Parsed activities: {len(result['activities'])}")


if __name__ == "__main__":
    main()