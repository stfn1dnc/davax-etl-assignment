-- =====================================================
-- T-09.4 - Timesheets Reconciliation
-- Compares the existing SOURCES and TARGET layers
-- =====================================================

SELECT
    'Source row count' AS metric,
    COUNT(*) AS metric_value
FROM sources.worked_hours_raw

UNION ALL

SELECT
    'Target row count',
    COUNT(*)
FROM target.fact_employee_activity f
JOIN target.dim_activity_type a
    ON a.activity_type_key = f.activity_type_key
WHERE a.activity_code = 'WORK'
  AND f.source_system = 'TIMESHEET'

UNION ALL

SELECT
    'Total hours source',
    NVL(SUM(worked_hours_raw), 0)
FROM sources.worked_hours_raw

UNION ALL

SELECT
    'Total hours target',
    NVL(SUM(f.hours), 0)
FROM target.fact_employee_activity f
JOIN target.dim_activity_type a
    ON a.activity_type_key = f.activity_type_key
WHERE a.activity_code = 'WORK'
  AND f.source_system = 'TIMESHEET'

UNION ALL

SELECT
    'Source rows missing from target',
    COUNT(*)
FROM sources.worked_hours_raw r
WHERE NOT EXISTS (
    SELECT 1
    FROM target.fact_employee_activity f
    JOIN target.dim_activity_type a
        ON a.activity_type_key = f.activity_type_key
    WHERE a.activity_code = 'WORK'
      AND f.source_system = 'TIMESHEET'
      AND f.source_record_id = TO_CHAR(r.worked_hours_raw_id)
)

UNION ALL

SELECT
    'Target rows missing from source',
    COUNT(*)
FROM target.fact_employee_activity f
JOIN target.dim_activity_type a
    ON a.activity_type_key = f.activity_type_key
WHERE a.activity_code = 'WORK'
  AND f.source_system = 'TIMESHEET'
  AND NOT EXISTS (
      SELECT 1
      FROM sources.worked_hours_raw r
      WHERE TO_CHAR(r.worked_hours_raw_id) = f.source_record_id
  );