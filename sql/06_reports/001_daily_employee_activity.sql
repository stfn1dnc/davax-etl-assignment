/* US-14: Daily employee activity report */

SELECT
    e.employee_id,
    e.employee_name,
    d.full_date AS activity_date,
    at.activity_code,
    at.activity_name,
    p.project_code AS project_name,
    t.training_name,
    f.hours,
    f.source_system,
    f.source_record_id
FROM target.fact_employee_activity f
JOIN target.dim_date d
    ON d.date_key = f.date_key
JOIN target.dim_activity_type at
    ON at.activity_type_key = f.activity_type_key
LEFT JOIN target.dim_employee e
    ON e.employee_key = f.employee_key
LEFT JOIN target.dim_project p
    ON p.project_key = f.project_key
LEFT JOIN target.dim_training t
    ON t.training_key = f.training_key
WHERE e.employee_id = :employee_id
  AND d.full_date = :selected_date
ORDER BY
    d.full_date,
    at.activity_code,
    p.project_code,
    t.training_name;