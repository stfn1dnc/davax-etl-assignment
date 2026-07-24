CREATE OR REPLACE PACKAGE staging.pkg_timesheet_absence_stage AS

    PROCEDURE load_staging(
        p_run_id IN NUMBER
    );

    PROCEDURE validate_staging(
        p_run_id IN NUMBER
    );

END pkg_timesheet_absence_stage;
/


CREATE OR REPLACE PACKAGE BODY staging.pkg_timesheet_absence_stage AS

    FUNCTION convert_to_date(
        p_value IN VARCHAR2
    ) RETURN DATE
    AS
    BEGIN
        RETURN TO_DATE(
            TRIM(p_value),
            'DD-MON-RR',
            'NLS_DATE_LANGUAGE=English'
        );

    EXCEPTION
        WHEN OTHERS THEN
            RETURN NULL;
    END convert_to_date;


    FUNCTION convert_to_number(
        p_value IN VARCHAR2
    ) RETURN NUMBER
    AS
    BEGIN
        RETURN TO_NUMBER(
            TRIM(p_value),
            '999999990D99',
            'NLS_NUMERIC_CHARACTERS=''.,'''
        );

    EXCEPTION
        WHEN OTHERS THEN
            RETURN NULL;
    END convert_to_number;


    PROCEDURE load_staging(
        p_run_id IN NUMBER
    )
    AS
        v_activity_date       DATE;
        v_absence_hours       NUMBER;
        v_validation_status   VARCHAR2(20);
        v_validation_message  VARCHAR2(500);
    BEGIN
        DELETE FROM staging.stg_timesheet_absence
        WHERE run_id = p_run_id;

        FOR r IN (
            SELECT
                timesheet_absence_raw_id,
                run_id,
                name_raw,
                email_raw,
                date_worked_raw,
                absence_hours_raw,
                project_code_raw,
                source_file_name,
                source_row_number
            FROM sources.timesheet_absence_raw
            WHERE run_id = p_run_id
            ORDER BY source_row_number
        )
        LOOP

            v_activity_date :=
                convert_to_date(r.date_worked_raw);

            v_absence_hours :=
                convert_to_number(r.absence_hours_raw);

            v_validation_status := 'VALID';

            v_validation_message :=
                'Source has no absence type; mapped to OTHER_ABSENCE.';


            IF TRIM(r.email_raw) IS NULL THEN

                v_validation_status := 'INVALID';
                v_validation_message := 'Employee email is missing.';

            ELSIF v_activity_date IS NULL THEN

                v_validation_status := 'INVALID';
                v_validation_message := 'DateWorked is invalid.';

            ELSIF v_absence_hours IS NULL THEN

                v_validation_status := 'INVALID';
                v_validation_message := 'AbsenceHours is invalid.';

            END IF;


            INSERT INTO staging.stg_timesheet_absence (
                timesheet_absence_raw_id,
                run_id,
                employee_name,
                employee_id_raw,
                activity_date,
                absence_hours,
                project_code,
                absence_type_code,
                source_file_name,
                source_row_number,
                validation_status,
                validation_message
            )
            VALUES (
                r.timesheet_absence_raw_id,
                r.run_id,
                TRIM(r.name_raw),
                LOWER(TRIM(r.email_raw)),
                v_activity_date,
                v_absence_hours,
                UPPER(TRIM(r.project_code_raw)),
                'OTHER_ABSENCE',
                r.source_file_name,
                r.source_row_number,
                v_validation_status,
                v_validation_message
            );

        END LOOP;

    END load_staging;

    PROCEDURE validate_staging(
    p_run_id IN NUMBER
    )
    AS
        v_invalid_rows NUMBER;
    BEGIN

        SELECT COUNT(*)
        INTO v_invalid_rows
        FROM staging.stg_timesheet_absence
        WHERE run_id = p_run_id
          AND validation_status = 'INVALID';

        DBMS_OUTPUT.PUT_LINE(
            'Invalid rows for run '
            || p_run_id
            || ': '
            || v_invalid_rows
        );

    END validate_staging;


END pkg_timesheet_absence_stage;
/

GRANT EXECUTE
ON staging.pkg_timesheet_absence_stage
TO sources;
/