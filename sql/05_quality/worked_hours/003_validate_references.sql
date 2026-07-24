-- =====================================================
-- T-09.3 - Validate References
-- =====================================================

-- Missing employee reference
SELECT
    r.worked_hours_raw_id,
    r.email_raw,
    r.project_code_raw,
    r.date_worked_raw,
    'Employee does not exist in DIM_EMPLOYEE' AS validation_error
FROM sources.worked_hours_raw r
LEFT JOIN target.dim_employee e
    ON UPPER(TRIM(e.employee_id)) = UPPER(TRIM(r.email_raw))
   AND e.employee_key <> 0
WHERE TRIM(r.email_raw) IS NOT NULL
  AND e.employee_key IS NULL

UNION ALL

-- Missing project reference
SELECT
    r.worked_hours_raw_id,
    r.email_raw,
    r.project_code_raw,
    r.date_worked_raw,
    'Project does not exist in DIM_PROJECT' AS validation_error
FROM sources.worked_hours_raw r
LEFT JOIN target.dim_project p
    ON UPPER(TRIM(p.project_code)) = UPPER(TRIM(r.project_code_raw))
   AND p.project_key <> 0
WHERE TRIM(r.project_code_raw) IS NOT NULL
  AND p.project_key IS NULL

UNION ALL

-- Missing date reference
SELECT
    r.worked_hours_raw_id,
    r.email_raw,
    r.project_code_raw,
    r.date_worked_raw,
    'Work date does not exist in DIM_DATE' AS validation_error
FROM sources.worked_hours_raw r
LEFT JOIN target.dim_date d
    ON d.full_date =
       TO_DATE(
           r.date_worked_raw DEFAULT NULL ON CONVERSION ERROR,
           'YYYY-MM-DD'
       )
WHERE TRIM(r.date_worked_raw) IS NOT NULL
  AND d.date_key IS NULL

ORDER BY
    worked_hours_raw_id,
    validation_error;