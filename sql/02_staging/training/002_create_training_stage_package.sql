CREATE OR REPLACE PACKAGE staging.pkg_training_stage AS

    FUNCTION parse_meeting_timestamp(
        p_value IN VARCHAR2
    ) RETURN TIMESTAMP;

    FUNCTION parse_duration_seconds(
        p_value IN VARCHAR2
    ) RETURN NUMBER;

    PROCEDURE load_staging(
        p_run_id IN NUMBER
    );

    PROCEDURE validate_staging(
        p_run_id IN NUMBER
    );

END pkg_training_stage;
/

CREATE OR REPLACE PACKAGE BODY staging.pkg_training_stage AS

    FUNCTION parse_meeting_timestamp(
        p_value IN VARCHAR2
    ) RETURN TIMESTAMP
    AS
        v_result TIMESTAMP;
    BEGIN
        IF TRIM(p_value) IS NULL THEN
            RETURN NULL;
        END IF;

        BEGIN
            v_result := TO_TIMESTAMP(
                TRIM(p_value),
                'MM/DD/RR, HH:MI:SS AM',
                'NLS_DATE_LANGUAGE=ENGLISH'
            );

            RETURN v_result;
        EXCEPTION
            WHEN OTHERS THEN
                NULL;
        END;

        BEGIN
            v_result := TO_TIMESTAMP(
                TRIM(p_value),
                'MM/DD/RR, HH:MI AM',
                'NLS_DATE_LANGUAGE=ENGLISH'
            );

            RETURN v_result;
        EXCEPTION
            WHEN OTHERS THEN
                RETURN NULL;
        END;
    END parse_meeting_timestamp;


    FUNCTION parse_duration_seconds(
        p_value IN VARCHAR2
    ) RETURN NUMBER
    AS
        v_hours NUMBER := 0;
        v_minutes NUMBER := 0;
        v_seconds NUMBER := 0;
        v_value VARCHAR2(200);
    BEGIN
        v_value := LOWER(TRIM(p_value));

        IF v_value IS NULL THEN
            RETURN NULL;
        END IF;

        v_hours := NVL(
            TO_NUMBER(
                REGEXP_SUBSTR(
                    v_value,
                    '([0-9]+)[[:space:]]*h',
                    1,
                    1,
                    'i',
                    1
                )
            ),
            0
        );

        v_minutes := NVL(
            TO_NUMBER(
                REGEXP_SUBSTR(
                    v_value,
                    '([0-9]+)[[:space:]]*m',
                    1,
                    1,
                    'i',
                    1
                )
            ),
            0
        );

        v_seconds := NVL(
            TO_NUMBER(
                REGEXP_SUBSTR(
                    v_value,
                    '([0-9]+)[[:space:]]*s',
                    1,
                    1,
                    'i',
                    1
                )
            ),
            0
        );

        RETURN
            (v_hours * 3600)
            + (v_minutes * 60)
            + v_seconds;

    EXCEPTION
        WHEN OTHERS THEN
            RETURN NULL;
    END parse_duration_seconds;


    PROCEDURE load_staging(
        p_run_id IN NUMBER
    )
    AS
    BEGIN
        DELETE FROM staging.stg_training_activity
        WHERE run_id = p_run_id;

        DELETE FROM staging.stg_training_participant
        WHERE run_id = p_run_id;

        DELETE FROM staging.stg_training_session
        WHERE run_id = p_run_id;


        INSERT INTO staging.stg_training_session (
            session_raw_id,
            run_id,
            session_source_key,
            meeting_title,
            reported_participant_count,
            start_timestamp,
            end_timestamp,
            meeting_duration_seconds,
            average_attendance_seconds,
            validation_status,
            validation_message
        )
        SELECT
            session_raw_id,
            run_id,
            session_source_key,
            TRIM(meeting_title_raw),

            CASE
                WHEN REGEXP_LIKE(
                    TRIM(attended_participants_raw),
                    '^[0-9]+$'
                )
                THEN TO_NUMBER(
                    attended_participants_raw
                )
                ELSE NULL
            END,

            parse_meeting_timestamp(start_time_raw),
            parse_meeting_timestamp(end_time_raw),
            parse_duration_seconds(meeting_duration_raw),
            parse_duration_seconds(
                average_attendance_time_raw
            ),

            CASE
                WHEN TRIM(meeting_title_raw) IS NULL
                  OR parse_meeting_timestamp(
                        start_time_raw
                     ) IS NULL
                  OR parse_meeting_timestamp(
                        end_time_raw
                     ) IS NULL
                THEN 'INVALID'
                ELSE 'VALID'
            END,

            CASE
                WHEN TRIM(meeting_title_raw) IS NULL
                THEN 'Meeting title is missing.'
                WHEN parse_meeting_timestamp(
                    start_time_raw
                ) IS NULL
                THEN 'Start timestamp is invalid.'
                WHEN parse_meeting_timestamp(
                    end_time_raw
                ) IS NULL
                THEN 'End timestamp is invalid.'
                ELSE NULL
            END

        FROM sources.training_session_raw
        WHERE run_id = p_run_id;


        INSERT INTO staging.stg_training_participant (
            participant_raw_id,
            session_raw_id,
            run_id,
            participant_name,
            email,
            participant_id,
            participant_role,
            first_join_timestamp,
            last_leave_timestamp,
            duration_seconds,
            validation_status,
            validation_message
        )
        SELECT
            participant_raw_id,
            session_raw_id,
            run_id,
            TRIM(participant_name_raw),
            LOWER(TRIM(email_raw)),
            TRIM(participant_id_raw),
            UPPER(TRIM(role_raw)),
            parse_meeting_timestamp(first_join_raw),
            parse_meeting_timestamp(last_leave_raw),
            parse_duration_seconds(
                in_meeting_duration_raw
            ),

            CASE
                WHEN TRIM(participant_name_raw) IS NULL
                     AND TRIM(email_raw) IS NULL
                     AND TRIM(participant_id_raw) IS NULL
                THEN 'INVALID'
                WHEN parse_duration_seconds(
                    in_meeting_duration_raw
                ) IS NULL
                THEN 'INVALID'
                ELSE 'VALID'
            END,

            CASE
                WHEN TRIM(participant_name_raw) IS NULL
                     AND TRIM(email_raw) IS NULL
                     AND TRIM(participant_id_raw) IS NULL
                THEN 'Participant identifier is missing.'
                WHEN parse_duration_seconds(
                    in_meeting_duration_raw
                ) IS NULL
                THEN 'Participant duration is invalid.'
                ELSE NULL
            END

        FROM sources.training_participant_raw
        WHERE run_id = p_run_id;


        INSERT INTO staging.stg_training_activity (
            activity_raw_id,
            session_raw_id,
            run_id,
            participant_name,
            email,
            participant_id,
            participant_role,
            join_timestamp,
            leave_timestamp,
            duration_seconds,
            validation_status,
            validation_message
        )
        SELECT
            activity_raw_id,
            session_raw_id,
            run_id,
            TRIM(participant_name_raw),
            LOWER(TRIM(email_raw)),
            TRIM(participant_id_raw),
            UPPER(TRIM(role_raw)),
            parse_meeting_timestamp(join_time_raw),
            parse_meeting_timestamp(leave_time_raw),
            parse_duration_seconds(duration_raw),

            CASE
                WHEN TRIM(participant_name_raw) IS NULL
                     AND TRIM(email_raw) IS NULL
                     AND TRIM(participant_id_raw) IS NULL
                THEN 'INVALID'
                WHEN parse_duration_seconds(
                    duration_raw
                ) IS NULL
                THEN 'INVALID'
                ELSE 'VALID'
            END,

            CASE
                WHEN TRIM(participant_name_raw) IS NULL
                     AND TRIM(email_raw) IS NULL
                     AND TRIM(participant_id_raw) IS NULL
                THEN 'Activity participant is missing.'
                WHEN parse_duration_seconds(
                    duration_raw
                ) IS NULL
                THEN 'Activity duration is invalid.'
                ELSE NULL
            END

        FROM sources.training_activity_raw
        WHERE run_id = p_run_id;

        COMMIT;
    END load_staging;


    PROCEDURE validate_staging(
        p_run_id IN NUMBER
    )
    AS
        v_checked NUMBER;
        v_failed NUMBER;
    BEGIN
        DELETE FROM etl_control.etl_error_log
        WHERE run_id = p_run_id
          AND pipeline_name = 'TRAINING_ATTENDANCE';

        DELETE FROM etl_control.data_quality_result
        WHERE run_id = p_run_id
          AND table_name LIKE 'STAGING.STG_TRAINING%';


        INSERT INTO etl_control.etl_error_log (
            run_id,
            pipeline_name,
            source_name,
            source_row_number,
            error_code,
            error_message,
            raw_record
        )
        SELECT
            p.run_id,
            'TRAINING_ATTENDANCE',
            r.source_file_name,
            r.source_row_number,
            'INVALID_PARTICIPANT',
            p.validation_message,
            r.raw_record
        FROM staging.stg_training_participant p
        JOIN sources.training_participant_raw r
          ON r.participant_raw_id =
             p.participant_raw_id
        WHERE p.run_id = p_run_id
          AND p.validation_status = 'INVALID';


        INSERT INTO etl_control.etl_error_log (
            run_id,
            pipeline_name,
            source_name,
            source_row_number,
            error_code,
            error_message,
            raw_record
        )
        SELECT
            a.run_id,
            'TRAINING_ATTENDANCE',
            r.source_file_name,
            r.source_row_number,
            'INVALID_ACTIVITY',
            a.validation_message,
            r.raw_record
        FROM staging.stg_training_activity a
        JOIN sources.training_activity_raw r
          ON r.activity_raw_id = a.activity_raw_id
        WHERE a.run_id = p_run_id
          AND a.validation_status = 'INVALID';


        SELECT COUNT(*),
               SUM(
                   CASE
                       WHEN validation_status = 'INVALID'
                       THEN 1
                       ELSE 0
                   END
               )
        INTO v_checked, v_failed
        FROM staging.stg_training_participant
        WHERE run_id = p_run_id;

        etl_control.pkg_etl_audit.log_quality_result(
            p_run_id,
            'TRAINING_PARTICIPANT_VALIDATION',
            'STAGING.STG_TRAINING_PARTICIPANT',
            NULL,
            CASE
                WHEN NVL(v_failed, 0) = 0
                THEN 'PASSED'
                ELSE 'FAILED'
            END,
            v_checked,
            NVL(v_failed, 0),
            'Checks participant identity and duration.'
        );


        SELECT COUNT(*),
               SUM(
                   CASE
                       WHEN validation_status = 'INVALID'
                       THEN 1
                       ELSE 0
                   END
               )
        INTO v_checked, v_failed
        FROM staging.stg_training_activity
        WHERE run_id = p_run_id;

        etl_control.pkg_etl_audit.log_quality_result(
            p_run_id,
            'TRAINING_ACTIVITY_VALIDATION',
            'STAGING.STG_TRAINING_ACTIVITY',
            NULL,
            CASE
                WHEN NVL(v_failed, 0) = 0
                THEN 'PASSED'
                ELSE 'FAILED'
            END,
            v_checked,
            NVL(v_failed, 0),
            'Checks activity participant and duration.'
        );


        SELECT COUNT(*)
        INTO v_failed
        FROM staging.stg_training_session s
        WHERE s.run_id = p_run_id
          AND s.reported_participant_count != (
              SELECT COUNT(*)
              FROM staging.stg_training_participant p
              WHERE p.session_raw_id =
                    s.session_raw_id
          );

        etl_control.pkg_etl_audit.log_quality_result(
            p_run_id,
            'REPORTED_VS_PARSED_PARTICIPANTS',
            'STAGING.STG_TRAINING_SESSION',
            'REPORTED_PARTICIPANT_COUNT',
            CASE
                WHEN v_failed = 0
                THEN 'PASSED'
                ELSE 'WARNING'
            END,
            1,
            v_failed,
            'Compares the summary participant count '
            || 'with parsed participant rows.'
        );

        COMMIT;
    END validate_staging;

END pkg_training_stage;
/