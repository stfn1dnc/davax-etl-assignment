
GRANT SELECT ON sources.exam_absence_raw TO staging;
GRANT SELECT, INSERT, DELETE ON etl_control.etl_error_log TO staging;
GRANT SELECT ON staging.stg_exam_absence TO sources;
