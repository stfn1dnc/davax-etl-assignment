
SET SERVEROUTPUT ON;

DEFINE timesheet_run_id = 1
DEFINE exam_run_id = 2

BEGIN
    target.pkg_absence_exam_target.load_timesheet_absences(
        p_run_id => &timesheet_run_id
    );

    target.pkg_absence_exam_target.load_exam_absences(
        p_run_id => &exam_run_id
    );

    COMMIT;
END;
/
