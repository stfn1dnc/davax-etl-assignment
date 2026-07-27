/* US-14: Monthly aggregated employee activity report */

WITH monthly_activity AS (
    SELECT
        e.employee_id,
        e.employee_name,
        d.year_number,
        d.month_number,
        d.month_name,
        at.activity_code,
        SUM(NVL(f.hours, 0)) AS total_hours,
        COUNT(*) AS activity_count
    FROM target.fact_employee_activity f
    JOIN target.dim_date d
        ON d.date_key = f.date_key
    JOIN target.dim_activity_type at
        ON at.activity_type_key = f.activity_type_key
    LEFT JOIN target.dim_employee e
        ON e.employee_key = f.employee_key
    GROUP BY
        e.employee_id,
        e.employee_name,
        d.year_number,
        d.month_number,
        d.month_name,
        at.activity_code
)
SELECT
    employee_id,
    employee_name,
    year_number,
    month_number,
    month_name,
    activity_code,
    total_hours,
    activity_count,
    DENSE_RANK() OVER (
        PARTITION BY year_number, month_number
        ORDER BY total_hours DESC
    ) AS monthly_rank
FROM monthly_activity
ORDER BY
    year_number,
    month_number,
    employee_name,
    activity_code;