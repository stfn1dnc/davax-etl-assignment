SELECT *
FROM staging.stg_employee
WHERE employee_id IS NULL

UNION ALL

SELECT *
FROM staging.stg_employee
WHERE employee_name IS NULL;