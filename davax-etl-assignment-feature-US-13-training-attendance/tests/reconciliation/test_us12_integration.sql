/*
===============================================================================
Story:       US-12
Purpose:     Integration and rerun test without deleting existing data.
Instructions:
    Replace the two run IDs below before running with F5.
===============================================================================
*/

SET SERVEROUTPUT ON;

DEFINE timesheet_run_id = 1
DEFINE exam_run_id = 2

DECLARE
    v_timesheet_stage_rows   NUMBER;
    v_timesheet_fact_first   NUMBER;
    v_timesheet_fact_second  NUMBER;
    v_timesheet_stage_hours  NUMBER;
    v_timesheet_fact_hours   NUMBER;

    v_exam_stage_rows        NUMBER;
    v_exam_fact_first        NUMBER;
    v_exam_fact_second       NUMBER;

    v_required_types         NUMBER;
    v_unknown_employee       NUMBER;
BEGIN
    ---------------------------------------------------------------------------
    -- Prerequisite checks.
    ---------------------------------------------------------------------------
    SELECT COUNT(*)
    INTO v_required_types
    FROM target.dim_activity_type
    WHERE activity_code IN (
        'ANNUAL_LEAVE',
        'SICK_LEAVE',
        'PUBLIC_HOLIDAY',
        'OTHER_ABSENCE',
        'DU_EXAM'
    );

    IF v_required_types <> 5 THEN
        RAISE_APPLICATION_ERROR(
            -20001,
            'Not all five US-12 activity types exist.'
        );
    END IF;

    SELECT COUNT(*)
    INTO v_unknown_employee
    FROM target.dim_employee
    WHERE employee_key = 0
      AND employee_id = 'UNKNOWN';

    IF v_unknown_employee <> 1 THEN
        RAISE_APPLICATION_ERROR(
            -20002,
            'The UNKNOWN employee record with employee_key 0 is missing.'
        );
    END IF;

    ---------------------------------------------------------------------------
    -- First load.
    ---------------------------------------------------------------------------
    target.pkg_absence_exam_target.load_timesheet_absences(
        &timesheet_run_id
    );

    target.pkg_absence_exam_target.load_exam_absences(
        &exam_run_id
    );

    SELECT COUNT(*), NVL(SUM(absence_hours), 0)
    INTO v_timesheet_stage_rows, v_timesheet_stage_hours
    FROM staging.stg_timesheet_absence
    WHERE run_id = &timesheet_run_id
      AND validation_status = 'VALID';

    SELECT COUNT(*), NVL(SUM(hours), 0)
    INTO v_timesheet_fact_first, v_timesheet_fact_hours
    FROM target.fact_employee_activity
    WHERE source_system = 'TIMESHEET_ABSENCES'
      AND etl_run_id = &timesheet_run_id;

    SELECT COUNT(*)
    INTO v_exam_stage_rows
    FROM staging.stg_exam_absence
    WHERE run_id = &exam_run_id
      AND validation_status = 'VALID';

    SELECT COUNT(*)
    INTO v_exam_fact_first
    FROM target.fact_employee_activity
    WHERE source_system = 'EXAM_ABSENCES'
      AND etl_run_id = &exam_run_id;

    IF v_timesheet_stage_rows <> v_timesheet_fact_first THEN
        RAISE_APPLICATION_ERROR(
            -20003,
            'Timesheet staging row count does not match fact row count.'
        );
    END IF;

    IF v_timesheet_stage_hours <> v_timesheet_fact_hours THEN
        RAISE_APPLICATION_ERROR(
            -20004,
            'Timesheet staging hours do not match fact hours.'
        );
    END IF;

    IF v_exam_stage_rows <> v_exam_fact_first THEN
        RAISE_APPLICATION_ERROR(
            -20005,
            'Exam staging row count does not match fact row count.'
        );
    END IF;

    ---------------------------------------------------------------------------
    -- Second load: counts must not increase.
    ---------------------------------------------------------------------------
    target.pkg_absence_exam_target.load_timesheet_absences(
        &timesheet_run_id
    );

    target.pkg_absence_exam_target.load_exam_absences(
        &exam_run_id
    );

    SELECT COUNT(*)
    INTO v_timesheet_fact_second
    FROM target.fact_employee_activity
    WHERE source_system = 'TIMESHEET_ABSENCES'
      AND etl_run_id = &timesheet_run_id;

    SELECT COUNT(*)
    INTO v_exam_fact_second
    FROM target.fact_employee_activity
    WHERE source_system = 'EXAM_ABSENCES'
      AND etl_run_id = &exam_run_id;

    IF v_timesheet_fact_first <> v_timesheet_fact_second THEN
        RAISE_APPLICATION_ERROR(
            -20006,
            'Timesheet rerun created duplicate fact rows.'
        );
    END IF;

    IF v_exam_fact_first <> v_exam_fact_second THEN
        RAISE_APPLICATION_ERROR(
            -20007,
            'Exam rerun created duplicate fact rows.'
        );
    END IF;

    DBMS_OUTPUT.PUT_LINE('US-12 integration test: PASSED');
    DBMS_OUTPUT.PUT_LINE(
        'Timesheet fact rows: ' || v_timesheet_fact_second
    );
    DBMS_OUTPUT.PUT_LINE(
        'Exam fact rows: ' || v_exam_fact_second
    );

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/
