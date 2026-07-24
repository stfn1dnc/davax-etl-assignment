

GRANT SELECT
ON staging.stg_timesheet_absence
TO target;

GRANT SELECT
ON staging.stg_exam_absence
TO target;

GRANT SELECT
ON target.fact_employee_activity
TO sources;
