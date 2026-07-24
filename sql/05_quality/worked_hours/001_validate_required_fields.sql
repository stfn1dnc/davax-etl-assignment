-- =====================================================
-- T-09.1 - Validate Required Fields
-- =====================================================

SELECT
    worked_hours_raw_id,
    email_raw,
    project_code_raw,
    date_worked_raw,
    worked_hours_raw,
    CASE
        WHEN TRIM(email_raw) IS NULL THEN 'Missing employee ID'
        WHEN TRIM(project_code_raw) IS NULL THEN 'Missing project ID'
        WHEN TRIM(date_worked_raw) IS NULL THEN 'Missing work date'
        WHEN worked_hours_raw IS NULL THEN 'Missing hours'
    END AS validation_error
FROM sources.worked_hours_raw
WHERE TRIM(email_raw) IS NULL
   OR TRIM(project_code_raw) IS NULL
   OR TRIM(date_worked_raw) IS NULL
   OR worked_hours_raw IS NULL
ORDER BY worked_hours_raw_id;