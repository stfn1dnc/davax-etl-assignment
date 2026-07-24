/* US-14: Training source-to-target reconciliation, matching grain */

SELECT
    dataset_name,
    source_count,
    staging_valid_count,
    staging_invalid_count,
    target_count,
    source_count - target_count AS difference,
    CASE
        WHEN source_count = target_count THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (
    SELECT
        'TRAINING_SESSION' AS dataset_name,
        (SELECT COUNT(*) FROM sources.training_session_raw) AS source_count,
        (SELECT COUNT(*) FROM staging.stg_training_session WHERE validation_status = 'VALID') AS staging_valid_count,
        (SELECT COUNT(*) FROM staging.stg_training_session WHERE validation_status = 'INVALID') AS staging_invalid_count,
        (SELECT COUNT(*) FROM target.dim_training) AS target_count
    FROM dual

    UNION ALL

    SELECT
        'TRAINING_PARTICIPANT' AS dataset_name,
        (SELECT COUNT(*) FROM sources.training_participant_raw) AS source_count,
        (SELECT COUNT(*) FROM staging.stg_training_participant WHERE validation_status = 'VALID') AS staging_valid_count,
        (SELECT COUNT(*) FROM staging.stg_training_participant WHERE validation_status = 'INVALID') AS staging_invalid_count,
        (SELECT COUNT(*) FROM target.fact_employee_activity WHERE 1 = 0) AS target_count
    FROM dual

    UNION ALL

    SELECT
        'TRAINING_ACTIVITY' AS dataset_name,
        (SELECT COUNT(*) FROM sources.training_activity_raw) AS source_count,
        (SELECT COUNT(*) FROM staging.stg_training_activity WHERE validation_status = 'VALID') AS staging_valid_count,
        (SELECT COUNT(*) FROM staging.stg_training_activity WHERE validation_status = 'INVALID') AS staging_invalid_count,
        (SELECT COUNT(*) FROM target.fact_employee_activity WHERE 1 = 0) AS target_count
    FROM dual
);