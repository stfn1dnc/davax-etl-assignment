-- =====================================================
-- T-09.2 - Validate Worked Hours
-- =====================================================

-- Rule 1 & 2: Individual record validation
SELECT
    worked_hours_raw_id,
    email_raw,
    date_worked_raw,
    worked_hours_raw,
    CASE
        WHEN worked_hours_raw <= 0 THEN 'Hours must be greater than 0'
        WHEN worked_hours_raw > 24 THEN 'Individual worked hours exceed 24'
    END AS validation_error
FROM sources.worked_hours_raw
WHERE worked_hours_raw <= 0
   OR worked_hours_raw > 24

UNION ALL

-- Rule 3: Total daily hours per employee
SELECT
    NULL AS worked_hours_raw_id,
    email_raw,
    date_worked_raw,
    SUM(worked_hours_raw) AS worked_hours_raw,
    'Daily total worked hours exceed 24' AS validation_error
FROM sources.worked_hours_raw
GROUP BY
    email_raw,
    date_worked_raw
HAVING SUM(worked_hours_raw) > 24

ORDER BY
    email_raw,
    date_worked_raw;