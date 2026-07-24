# Timesheet Absences Data Profile

## User story

US-10 – Timesheet Absences profiling and ingestion.

## Source file

`Timesheet_Absences 1.csv`

The original file must remain unchanged and should be stored locally in
`data/input/`. It should not be committed if the project data is confidential.

## Physical profile

- Encoding: UTF-8 with optional BOM (`utf-8-sig`)
- Delimiter: comma (`,`)
- Rows: 63 data rows
- Columns: 5
- Null or blank values: 0 in all columns
- Exact duplicate rows: 0

## Columns

| Source column | Meaning | Raw target column |
|---|---|---|
| `Name` | Employee display name | `name_raw` |
| `Email` | Employee identifier candidate | `email_raw` |
| `DateWorked` | Activity date | `date_worked_raw` |
| `AbsenceHours` | Number of absence hours | `absence_hours_raw` |
| `ProjectCode` | Project code present in the export | `project_code_raw` |

## Business profiling

- Employee key candidate: `Email`
- Candidate row key: `Email + DateWorked + ProjectCode`
- Unique employees: 21
- Date structure: one date per row; no start/end interval
- Date format: `DD-MON-RR`, English month abbreviation
- Date range: 2025-06-24 to 2025-06-26
- Absence hours range: 0.51 to 2.95
- Total absence hours: 108.08
- Project codes: `PRJ101`, `PRJ102`, `PRJ103`

## Absence type finding

The source does **not** contain an absence type column. `ProjectCode` must not be
interpreted as an absence type because the source provides no evidence for such
a mapping.

Documented temporary assumption for US-10:

- `absence_type_code = OTHER_ABSENCE` for every valid source row.
- This assumption must be confirmed with the mentor before US-12 target loading.
- When a real source type becomes available, the staging mapping must be updated.

## Interval expansion

No interval expansion is performed because the source contains `DateWorked`
only. The US-10 rule says to expand intervals only when the source provides a
start and end date.

## Layer mapping

```text
Timesheet_Absences CSV
        -> SOURCES.TIMESHEET_ABSENCE_RAW
        -> STAGING.STG_TIMESHEET_ABSENCE
```

