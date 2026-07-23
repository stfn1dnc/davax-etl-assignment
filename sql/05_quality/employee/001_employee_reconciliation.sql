SELECT
    'RAW' AS layer_name,
    COUNT(*) AS row_count
FROM sources.employee_master_raw

UNION ALL

SELECT
    'STAGING',
    COUNT(*)
FROM staging.stg_employee

UNION ALL

SELECT
    'TARGET',
    COUNT(*)
FROM target.dim_employee;