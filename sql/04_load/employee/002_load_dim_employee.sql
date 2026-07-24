MERGE INTO target.dim_employee target
USING (
    SELECT
        employee_id,
        employee_name,
        grade,
        discipline,
        line_manager,
        delivery_unit,
        dataset_name,
        process_timestamp
    FROM staging.stg_employee
    WHERE validation_status = 'VALID'
) source
ON (
    target.employee_id = source.employee_id
)
WHEN MATCHED THEN
    UPDATE SET
        target.employee_name = source.employee_name,
        target.grade = source.grade,
        target.discipline = source.discipline,
        target.line_manager = source.line_manager,
        target.delivery_unit = source.delivery_unit,
        target.dataset_name = source.dataset_name,
        target.process_timestamp = source.process_timestamp
WHEN NOT MATCHED THEN
    INSERT (
        employee_id,
        employee_name,
        grade,
        discipline,
        line_manager,
        delivery_unit,
        dataset_name,
        process_timestamp
    )
    VALUES (
        source.employee_id,
        source.employee_name,
        source.grade,
        source.discipline,
        source.line_manager,
        source.delivery_unit,
        source.dataset_name,
        source.process_timestamp
    );