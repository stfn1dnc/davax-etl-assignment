SELECT
    raw.raw_rows,
    fact.fact_rows,
    raw.raw_hours,
    fact.fact_hours,
    raw.raw_rows - fact.fact_rows AS row_difference,
    raw.raw_hours - fact.fact_hours AS hours_difference
FROM
(
    SELECT
        COUNT(*) AS raw_rows,
        SUM(worked_hours_raw) AS raw_hours
    FROM sources.worked_hours_raw
    WHERE worked_hours_raw IS NOT NULL
      AND worked_hours_raw >= 0
) raw
CROSS JOIN
(
    SELECT
        COUNT(*) AS fact_rows,
        SUM(hours) AS fact_hours
    FROM target.fact_employee_activity
    WHERE source_system = 'TIMESHEET'
) fact;