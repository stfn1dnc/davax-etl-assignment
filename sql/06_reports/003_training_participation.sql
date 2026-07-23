/* US-14: Training participation report */

SELECT
    e.employee_id,
    e.employee_name,
    d.full_date AS training_date,
    t.training_name,
    f.hours,
    f.source_record_id
FROM target.fact_employee_activity f
JOIN target.dim_date d
    ON d.date_key = f.date_key
JOIN target.dim_activity_type at
    ON at.activity_type_key = f.activity_type_key
LEFT JOIN target.dim_employee e
    ON e.employee_key = f.employee_key
LEFT JOIN target.dim_training t
    ON t.training_key = f.training_key
WHERE at.activity_code = 'TRAINING'
ORDER BY
    d.full_date,
    e.employee_name,
    t.training_name;