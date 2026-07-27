/* US-14: Employees without activity report */

SELECT
    e.employee_id,
    e.employee_name,
    e.grade,
    e.discipline,
    e.line_manager,
    e.delivery_unit
FROM target.dim_employee e
LEFT JOIN target.fact_employee_activity f
    ON f.employee_key = e.employee_key
WHERE f.employee_key IS NULL
  AND e.employee_id <> 'UNKNOWN'
ORDER BY
    e.employee_name;