

CREATE OR REPLACE PACKAGE target.pkg_absence_exam_target AS

    PROCEDURE load_timesheet_absences(
        p_run_id IN NUMBER
    );

    PROCEDURE load_exam_absences(
        p_run_id IN NUMBER
    );

END pkg_absence_exam_target;
/


CREATE OR REPLACE PACKAGE BODY target.pkg_absence_exam_target AS

    PROCEDURE load_timesheet_absences(
        p_run_id IN NUMBER
    )
    AS
        v_inserted_rows NUMBER;
    BEGIN
        INSERT INTO target.fact_employee_activity (
            employee_key,
            date_key,
            activity_type_key,
            project_key,
            training_key,
            source_system,
            source_record_id,
            hours,
            etl_run_id
        )
        SELECT
            NVL(
                employee_by_id.employee_key,
                NVL(employee_by_name.employee_key, 0)
            ) AS employee_key,
            date_dimension.date_key,
            activity_type.activity_type_key,
            NULL AS project_key,
            NULL AS training_key,
            'TIMESHEET_ABSENCES' AS source_system,
            TO_CHAR(stage_row.timesheet_absence_raw_id) AS source_record_id,
            NVL(stage_row.absence_hours, 0) AS hours,
            stage_row.run_id AS etl_run_id
        FROM staging.stg_timesheet_absence stage_row

        LEFT JOIN (
            SELECT
                LOWER(TRIM(employee_id)) AS employee_id_normalized,
                MIN(employee_key) AS employee_key
            FROM target.dim_employee
            GROUP BY LOWER(TRIM(employee_id))
        ) employee_by_id
          ON employee_by_id.employee_id_normalized =
             LOWER(TRIM(stage_row.employee_id_raw))

        LEFT JOIN (
            SELECT
                UPPER(TRIM(employee_name)) AS employee_name_normalized,
                MIN(employee_key) AS employee_key
            FROM target.dim_employee
            WHERE employee_key <> 0
            GROUP BY UPPER(TRIM(employee_name))
        ) employee_by_name
          ON employee_by_name.employee_name_normalized =
             UPPER(TRIM(stage_row.employee_name))

        JOIN target.dim_date date_dimension
          ON date_dimension.full_date = TRUNC(stage_row.activity_date)

        JOIN target.dim_activity_type activity_type
          ON activity_type.activity_code =
             UPPER(TRIM(stage_row.absence_type_code))

        WHERE stage_row.run_id = p_run_id
          AND stage_row.validation_status = 'VALID'
          AND NOT EXISTS (
                SELECT 1
                FROM target.fact_employee_activity fact_row
                WHERE fact_row.source_system = 'TIMESHEET_ABSENCES'
                  AND fact_row.source_record_id =
                      TO_CHAR(stage_row.timesheet_absence_raw_id)
                  AND fact_row.activity_type_key =
                      activity_type.activity_type_key
          );

        v_inserted_rows := SQL%ROWCOUNT;

        DBMS_OUTPUT.PUT_LINE(
            'Timesheet Absences rows inserted: ' || v_inserted_rows
        );
    END load_timesheet_absences;

    PROCEDURE load_exam_absences(
        p_run_id IN NUMBER
    )
    AS
        v_inserted_rows NUMBER;
    BEGIN
        INSERT INTO target.fact_employee_activity (
            employee_key,
            date_key,
            activity_type_key,
            project_key,
            training_key,
            source_system,
            source_record_id,
            hours,
            etl_run_id
        )
        SELECT
            NVL(employee_by_name.employee_key, 0) AS employee_key,
            date_dimension.date_key,
            activity_type.activity_type_key,
            NULL AS project_key,
            NULL AS training_key,
            'EXAM_ABSENCES' AS source_system,
            TO_CHAR(stage_row.exam_absence_raw_id) AS source_record_id,
            0 AS hours,
            stage_row.run_id AS etl_run_id
        FROM staging.stg_exam_absence stage_row

        LEFT JOIN (
            SELECT
                UPPER(TRIM(employee_name)) AS employee_name_normalized,
                MIN(employee_key) AS employee_key
            FROM target.dim_employee
            WHERE employee_key <> 0
            GROUP BY UPPER(TRIM(employee_name))
        ) employee_by_name
          ON employee_by_name.employee_name_normalized =
             UPPER(TRIM(stage_row.employee_id_raw))

        JOIN target.dim_date date_dimension
          ON date_dimension.full_date = TRUNC(stage_row.activity_date)

        JOIN target.dim_activity_type activity_type
          ON activity_type.activity_code = 'DU_EXAM'

        WHERE stage_row.run_id = p_run_id
          AND stage_row.validation_status = 'VALID'
          AND NOT EXISTS (
                SELECT 1
                FROM target.fact_employee_activity fact_row
                WHERE fact_row.source_system = 'EXAM_ABSENCES'
                  AND fact_row.source_record_id =
                      TO_CHAR(stage_row.exam_absence_raw_id)
                  AND fact_row.activity_type_key =
                      activity_type.activity_type_key
          );

        v_inserted_rows := SQL%ROWCOUNT;

        DBMS_OUTPUT.PUT_LINE(
            'Exam Absences rows inserted: ' || v_inserted_rows
        );
    END load_exam_absences;

END pkg_absence_exam_target;
/

GRANT EXECUTE
ON target.pkg_absence_exam_target
TO sources;
