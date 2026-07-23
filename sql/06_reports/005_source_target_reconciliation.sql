/* US-14: Source to target reconciliation */

SELECT
    dataset_name,
    source_count,
    staging_valid_count,
    staging_invalid_count,
    target_count,
    (source_count - target_count) AS difference,
    CASE
        WHEN source_count = target_count THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (
    SELECT
        'TRAINING_ATTENDANCE' AS dataset_name,
        (SELECT COUNT(*) FROM sources.training_session_raw) AS source_count,
        (SELECT COUNT(*) FROM staging.stg_training_participant) AS staging_valid_count,
        (SELECT COUNT(*)
         FROM staging.stg_training_participant
         WHERE validation_status = 'INVALID') AS staging_invalid_count,
        (SELECT COUNT(*)
         FROM target.fact_employee_activity f
         JOIN target.dim_activity_type at
           ON at.activity_type_key = f.activity_type_key
         WHERE at.activity_code = 'TRAINING') AS target_count
    FROM dual
);