-- =====================================================
-- T-09.5 - Monthly Working Hours Report
-- Source: TARGET star schema
-- Output: employee, year, month, project, total_hours
-- =====================================================

SELECT
    e.employee_name AS employee,
    d.year_number   AS year,
    d.month_number  AS month,
    p.project_code  AS project,
    SUM(f.hours)    AS total_hours
FROM target.fact_employee_activity f
JOIN target.dim_employee e
    ON e.employee_key = f.employee_key
JOIN target.dim_date d
    ON d.date_key = f.date_key
JOIN target.dim_project p
    ON p.project_key = f.project_key
JOIN target.dim_activity_type a
    ON a.activity_type_key = f.activity_type_key
WHERE a.activity_code = 'WORK'
  AND f.source_system = 'TIMESHEET'
GROUP BY
    e.employee_name,
    d.year_number,
    d.month_number,
    p.project_code
ORDER BY
    d.year_number,
    d.month_number,
    e.employee_name,
    p.project_code;