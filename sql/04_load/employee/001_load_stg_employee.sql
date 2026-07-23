INSERT INTO staging.stg_employee
(
    employee_id,
    employee_name,
    grade,
    discipline,
    line_manager,
    delivery_unit,
    validation_status,
    validation_message,
    dataset_name,
    source_file_name,
    process_timestamp
)

SELECT

    LOWER(TRIM(employee_id)),

    TRIM(employee_name),

    UPPER(TRIM(grade)),

    UPPER(TRIM(discipline)),

    TRIM(line_manager),

    UPPER(TRIM(delivery_unit)),

    'VALID',

    NULL,

    dataset_name,

    source_file_name,

    process_timestamp

FROM sources.employee_master_raw;