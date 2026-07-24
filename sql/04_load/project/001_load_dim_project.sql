MERGE INTO target.dim_project target
USING
(
    SELECT DISTINCT
        UPPER(TRIM(project_code_raw)) AS project_code,
        dataset_name,
        process_timestamp
    FROM sources.worked_hours_raw
    WHERE project_code_raw IS NOT NULL
      AND TRIM(project_code_raw) IS NOT NULL
) source
ON
(
    target.project_code = source.project_code
)
WHEN MATCHED THEN
UPDATE SET
    target.dataset_name = source.dataset_name,
    target.process_timestamp = source.process_timestamp
WHEN NOT MATCHED THEN
INSERT
(
    project_code,
    dataset_name,
    process_timestamp
)
VALUES
(
    source.project_code,
    source.dataset_name,
    source.process_timestamp
);

COMMIT;