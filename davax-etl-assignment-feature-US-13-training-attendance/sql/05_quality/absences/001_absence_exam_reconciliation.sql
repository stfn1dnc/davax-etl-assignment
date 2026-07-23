
DEFINE timesheet_run_id = 1
DEFINE exam_run_id = 2

PROMPT === TIMESHEET ABSENCE ROW AND HOURS RECONCILIATION ===

SELECT
    stage_values.staging_rows,
    fact_values.fact_rows,
    stage_values.staging_hours,
    fact_values.fact_hours,
    fact_values.unknown_employee_rows,
    CASE
        WHEN stage_values.staging_rows = fact_values.fact_rows
         AND stage_values.staging_hours = fact_values.fact_hours
        THEN 'MATCH'
        ELSE 'MISMATCH'
    END AS reconciliation_status
FROM (
    SELECT
        COUNT(*) AS staging_rows,
        NVL(SUM(absence_hours), 0) AS staging_hours
    FROM staging.stg_timesheet_absence
    WHERE run_id = &timesheet_run_id
      AND validation_status = 'VALID'
) stage_values
CROSS JOIN (
    SELECT
        COUNT(*) AS fact_rows,
        NVL(SUM(hours), 0) AS fact_hours,
        NVL(SUM(CASE WHEN employee_key = 0 THEN 1 ELSE 0 END), 0)
            AS unknown_employee_rows
    FROM target.fact_employee_activity
    WHERE source_system = 'TIMESHEET_ABSENCES'
      AND etl_run_id = &timesheet_run_id
) fact_values;


PROMPT === TIMESHEET ABSENCE DISTINCT DAY RECONCILIATION ===
PROMPT This comparison is fully meaningful when UNKNOWN_EMPLOYEE_ROWS = 0.

SELECT
    stage_days.staging_absence_days,
    fact_days.fact_absence_days,
    CASE
        WHEN stage_days.staging_absence_days = fact_days.fact_absence_days
        THEN 'MATCH'
        ELSE 'MISMATCH'
    END AS reconciliation_status
FROM (
    SELECT COUNT(*) AS staging_absence_days
    FROM (
        SELECT DISTINCT
            LOWER(TRIM(employee_id_raw)) AS employee_id_raw,
            TRUNC(activity_date) AS activity_date
        FROM staging.stg_timesheet_absence
        WHERE run_id = &timesheet_run_id
          AND validation_status = 'VALID'
    )
) stage_days
CROSS JOIN (
    SELECT COUNT(*) AS fact_absence_days
    FROM (
        SELECT DISTINCT
            employee_key,
            date_key
        FROM target.fact_employee_activity
        WHERE source_system = 'TIMESHEET_ABSENCES'
          AND etl_run_id = &timesheet_run_id
    )
) fact_days;


PROMPT === EXAM ROW / MATRIX CELL RECONCILIATION ===

SELECT
    stage_values.staging_exam_rows,
    fact_values.fact_exam_rows,
    fact_values.unknown_employee_rows,
    CASE
        WHEN stage_values.staging_exam_rows = fact_values.fact_exam_rows
        THEN 'MATCH'
        ELSE 'MISMATCH'
    END AS reconciliation_status
FROM (
    SELECT COUNT(*) AS staging_exam_rows
    FROM staging.stg_exam_absence
    WHERE run_id = &exam_run_id
      AND validation_status = 'VALID'
) stage_values
CROSS JOIN (
    SELECT
        COUNT(*) AS fact_exam_rows,
        NVL(SUM(CASE WHEN employee_key = 0 THEN 1 ELSE 0 END), 0)
            AS unknown_employee_rows
    FROM target.fact_employee_activity
    WHERE source_system = 'EXAM_ABSENCES'
      AND etl_run_id = &exam_run_id
) fact_values;
