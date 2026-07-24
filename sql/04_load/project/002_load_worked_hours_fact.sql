MERGE INTO target.fact_employee_activity target
USING (
    SELECT
        NVL(employee.employee_key, 0) AS employee_key,
        date_dimension.date_key,
        activity.activity_type_key,
        NVL(project.project_key, 0) AS project_key,
        CAST(NULL AS NUMBER) AS training_key,
        'TIMESHEET' AS source_system,
        TO_CHAR(raw.worked_hours_raw_id) AS source_record_id,
        raw.worked_hours_raw AS hours,
        raw.run_id AS etl_run_id
    FROM sources.worked_hours_raw raw
    LEFT JOIN target.dim_employee employee
        ON LOWER(TRIM(employee.employee_id)) = LOWER(TRIM(raw.email_raw))
    JOIN target.dim_date date_dimension
        ON date_dimension.full_date = TO_DATE(raw.date_worked_raw, 'YYYY-MM-DD')
    LEFT JOIN target.dim_project project
        ON project.project_code = UPPER(TRIM(raw.project_code_raw))
    JOIN target.dim_activity_type activity
        ON activity.activity_code = 'WORK'
    WHERE raw.date_worked_raw IS NOT NULL
      AND REGEXP_LIKE(raw.date_worked_raw, '^\d{4}-\d{2}-\d{2}$')
      AND raw.worked_hours_raw IS NOT NULL
      AND raw.worked_hours_raw >= 0
) source
ON (
    target.source_system = source.source_system
    AND target.source_record_id = source.source_record_id
    AND target.activity_type_key = source.activity_type_key
)
WHEN NOT MATCHED THEN
INSERT (
    employee_key,
    date_key,
    activity_type_key,
    project_key,
    training_key,
    source_system,
    source_record_id,
    hours,
    etl_run_id
)
VALUES (
    source.employee_key,
    source.date_key,
    source.activity_type_key,
    source.project_key,
    source.training_key,
    source.source_system,
    source.source_record_id,
    source.hours,
    source.etl_run_id
);