CREATE OR REPLACE PACKAGE target.pkg_training_target AS

    PROCEDURE load_dim_training(
        p_run_id IN NUMBER
    );

END pkg_training_target;
/

CREATE OR REPLACE PACKAGE BODY target.pkg_training_target AS

    PROCEDURE load_dim_training(
        p_run_id IN NUMBER
    )
    AS
    BEGIN
        MERGE INTO target.dim_training target_row
        USING (
            SELECT
                session_source_key,
                meeting_title,
                start_timestamp,
                end_timestamp,
                reported_participant_count,
                TO_CHAR(session_raw_id)
                    AS source_record_id
            FROM staging.stg_training_session
            WHERE run_id = p_run_id
              AND validation_status = 'VALID'
        ) source_row
        ON (
            target_row.training_source_key =
            source_row.session_source_key
        )

        WHEN MATCHED THEN
            UPDATE SET
                target_row.training_name =
                    source_row.meeting_title,
                target_row.session_start_timestamp =
                    source_row.start_timestamp,
                target_row.session_end_timestamp =
                    source_row.end_timestamp,
                target_row.reported_participant_count =
                    source_row.reported_participant_count,
                target_row.load_timestamp =
                    SYSTIMESTAMP

        WHEN NOT MATCHED THEN
            INSERT (
                training_source_key,
                training_name,
                session_start_timestamp,
                session_end_timestamp,
                reported_participant_count,
                source_system,
                source_record_id
            )
            VALUES (
                source_row.session_source_key,
                source_row.meeting_title,
                source_row.start_timestamp,
                source_row.end_timestamp,
                source_row.reported_participant_count,
                'MEETING_ATTENDANCE',
                source_row.source_record_id
            );

        COMMIT;
    END load_dim_training;

END pkg_training_target;
/