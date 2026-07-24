# Exam Absences data profile

## Source file
`Exam_Absences 1.csv`

## Detected structure
The real file is **wide / matrix**.

- Employee column: `Name`
- Date columns: `D_DD_MM_YYYY`
- Employee rows: 327
- Date columns: 14
- Date range: 19 May 2025 - 1 June 2025
- Exact duplicate rows: 0
- Duplicate employee names: 0
- Missing employee names: 0

## Cell values
The real matrix contains only `0` to `9`.

- `0`: treated as no exam absence and not converted to an activity row
- `1` to `9`: preserved as `activity_code_raw`
- The business meaning of each numeric code is not provided by the source
- Any other non-empty code is logged as `UNKNOWN_ACTIVITY_CODE`

The real file contains 1,586 non-zero activity cells, so the expected canonical RAW row count is 1,586.

## Employee identifier
The source provides no employee ID or email. `Name` is used temporarily as `employee_id_raw`.
Resolution to `TARGET.DIM_EMPLOYEE.employee_key` belongs to US-12.

## Canonical format
Both matrix and long input are normalized to:

- `employee_id_raw`
- `activity_date_raw`
- `activity_code_raw`
- `source_file_name`
- `source_row_number`
- `source_column_name`
- `run_id`

Common metadata also includes `dataset_name`, `source_file_hash`, `raw_record`, and `process_timestamp`.

## Matrix transformation
The Python parser uses `pandas.melt()`.

- `source_row_number` is the original employee row
- `source_column_name` is the original date column
- `activity_date_raw` preserves the original date column value
- empty and `0` cells are ignored

## Long input
A long file is accepted when it contains employee, date, and activity code columns. It is normalized without `melt()`.

## Staging rules
The PL/SQL package:

- converts matrix and long date formats to Oracle `DATE`
- trims and uppercases the employee value
- accepts codes `1` to `9`
- skips invalid rows from staging
- prevents duplicate employee/date/activity rows
- logs missing employees, invalid dates, unknown codes, and duplicates
