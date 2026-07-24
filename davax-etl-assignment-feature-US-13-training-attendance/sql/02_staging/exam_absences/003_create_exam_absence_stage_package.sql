CREATE OR REPLACE PACKAGE staging.pkg_exam_absence_stage AS
    PROCEDURE load_staging(p_run_id IN NUMBER);
    PROCEDURE validate_staging(p_run_id IN NUMBER);
END pkg_exam_absence_stage;
/

CREATE OR REPLACE PACKAGE BODY staging.pkg_exam_absence_stage AS

    FUNCTION convert_to_date(p_value IN VARCHAR2) RETURN DATE AS
        v_value VARCHAR2(100);
    BEGIN
        v_value := TRIM(p_value);

        IF REGEXP_LIKE(v_value, '^D_[0-9]{2}_[0-9]{2}_[0-9]{4}$', 'i') THEN
            RETURN TO_DATE(SUBSTR(v_value, 3), 'DD_MM_YYYY');
        END IF;

        IF REGEXP_LIKE(v_value, '^[0-9]{4}-[0-9]{2}-[0-9]{2}$') THEN
            RETURN TO_DATE(v_value, 'YYYY-MM-DD');
        END IF;

        RETURN TO_DATE(v_value, 'DD-MM-YYYY');
    EXCEPTION
        WHEN OTHERS THEN
            RETURN NULL;
    END convert_to_date;

    FUNCTION valid_activity_code(p_value IN VARCHAR2) RETURN BOOLEAN AS
    BEGIN
        RETURN REGEXP_LIKE(TRIM(p_value), '^[1-9]$');
    END valid_activity_code;

    PROCEDURE load_staging(p_run_id IN NUMBER) AS
        v_activity_date DATE;
        v_duplicate_count NUMBER;
    BEGIN
        DELETE FROM staging.stg_exam_absence
        WHERE run_id = p_run_id;

        FOR r IN (
            SELECT
                exam_absence_raw_id,
                run_id,
                employee_id_raw,
                activity_date_raw,
                activity_code_raw,
                source_file_name,
                source_row_number,
                source_column_name
            FROM sources.exam_absence_raw
            WHERE run_id = p_run_id
            ORDER BY exam_absence_raw_id
        )
        LOOP
            v_activity_date := convert_to_date(r.activity_date_raw);

            IF TRIM(r.employee_id_raw) IS NOT NULL
               AND v_activity_date IS NOT NULL
               AND valid_activity_code(r.activity_code_raw)
            THEN
                SELECT COUNT(*)
                INTO v_duplicate_count
                FROM staging.stg_exam_absence
                WHERE run_id = r.run_id
                  AND employee_id_raw = UPPER(TRIM(r.employee_id_raw))
                  AND activity_date = v_activity_date
                  AND activity_code = TRIM(r.activity_code_raw);

                IF v_duplicate_count = 0 THEN
                    INSERT INTO staging.stg_exam_absence (
                        exam_absence_raw_id,
                        run_id,
                        employee_id_raw,
                        activity_date,
                        activity_code,
                        source_file_name,
                        source_row_number,
                        source_column_name,
                        validation_status
                    )
                    VALUES (
                        r.exam_absence_raw_id,
                        r.run_id,
                        UPPER(TRIM(r.employee_id_raw)),
                        v_activity_date,
                        TRIM(r.activity_code_raw),
                        r.source_file_name,
                        r.source_row_number,
                        r.source_column_name,
                        'VALID'
                    );
                END IF;
            END IF;
        END LOOP;
    END load_staging;

    PROCEDURE validate_staging(p_run_id IN NUMBER) AS
        v_activity_date DATE;
        v_previous_count NUMBER;
        v_error_code VARCHAR2(100);
        v_error_message VARCHAR2(4000);
    BEGIN
        DELETE FROM etl_control.etl_error_log
        WHERE run_id = p_run_id
          AND pipeline_name = 'EXAM_ABSENCES';

        FOR r IN (
            SELECT
                exam_absence_raw_id,
                run_id,
                employee_id_raw,
                activity_date_raw,
                activity_code_raw,
                source_file_name,
                source_row_number,
                raw_record
            FROM sources.exam_absence_raw
            WHERE run_id = p_run_id
            ORDER BY exam_absence_raw_id
        )
        LOOP
            v_activity_date := convert_to_date(r.activity_date_raw);
            v_error_code := NULL;
            v_error_message := NULL;

            IF TRIM(r.employee_id_raw) IS NULL THEN
                v_error_code := 'MISSING_EMPLOYEE';
                v_error_message := 'Employee identifier is missing.';

            ELSIF v_activity_date IS NULL THEN
                v_error_code := 'INVALID_DATE';
                v_error_message := 'Activity date is invalid: ' || r.activity_date_raw;

            ELSIF NOT valid_activity_code(r.activity_code_raw) THEN
                v_error_code := 'UNKNOWN_ACTIVITY_CODE';
                v_error_message := 'Unknown activity code: ' || r.activity_code_raw;

            ELSE
                SELECT COUNT(*)
                INTO v_previous_count
                FROM staging.stg_exam_absence stage_row
                WHERE stage_row.run_id = r.run_id
                  AND stage_row.employee_id_raw = UPPER(TRIM(r.employee_id_raw))
                  AND stage_row.activity_date = v_activity_date
                  AND stage_row.activity_code = TRIM(r.activity_code_raw)
                  AND stage_row.exam_absence_raw_id <> r.exam_absence_raw_id;

                IF v_previous_count > 0 THEN
                    v_error_code := 'DUPLICATE_ACTIVITY';
                    v_error_message := 'Duplicate employee/date/activity row.';
                END IF;
            END IF;

            IF v_error_code IS NOT NULL THEN
                INSERT INTO etl_control.etl_error_log (
                    run_id,
                    pipeline_name,
                    source_name,
                    source_row_number,
                    error_code,
                    error_message,
                    raw_record
                )
                VALUES (
                    r.run_id,
                    'EXAM_ABSENCES',
                    r.source_file_name,
                    r.source_row_number,
                    v_error_code,
                    v_error_message,
                    r.raw_record
                );
            END IF;
        END LOOP;
    END validate_staging;

END pkg_exam_absence_stage;
/

GRANT EXECUTE ON staging.pkg_exam_absence_stage TO sources;
/
