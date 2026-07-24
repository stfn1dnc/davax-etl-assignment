
MERGE INTO target.dim_activity_type target_row
USING (
    SELECT 'ANNUAL_LEAVE' AS activity_code,
           'Annual Leave' AS activity_name,
           'Annual leave absence.' AS description
    FROM dual

    UNION ALL

    SELECT 'SICK_LEAVE',
           'Sick Leave',
           'Medical or sick leave absence.'
    FROM dual

    UNION ALL

    SELECT 'PUBLIC_HOLIDAY',
           'Public Holiday',
           'Public holiday absence.'
    FROM dual

    UNION ALL

    SELECT 'OTHER_ABSENCE',
           'Other Absence',
           'Absence that cannot be classified more specifically.'
    FROM dual

    UNION ALL

    SELECT 'DU_EXAM',
           'DU Exam',
           'Exam activity from the DU Exam Absences source.'
    FROM dual
) source_row
ON (
    target_row.activity_code = source_row.activity_code
)
WHEN NOT MATCHED THEN
    INSERT (
        activity_code,
        activity_name,
        description
    )
    VALUES (
        source_row.activity_code,
        source_row.activity_name,
        source_row.description
    );

COMMIT;
