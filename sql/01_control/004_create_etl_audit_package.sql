--PACKAGE SPECIFICATION
CREATE OR REPLACE PACKAGE etl_control.pkg_etl_audit AS

    PROCEDURE start_run(
        p_pipeline_name IN VARCHAR2,
        p_source_name   IN VARCHAR2,
        p_run_id        OUT NUMBER
    );

    PROCEDURE finish_run_success(
        p_run_id         IN NUMBER,
        p_rows_read      IN NUMBER,
        p_rows_loaded    IN NUMBER,
        p_rows_rejected  IN NUMBER
    );

    PROCEDURE finish_run_failed(
        p_run_id         IN NUMBER,
        p_rows_read      IN NUMBER,
        p_rows_loaded    IN NUMBER,
        p_rows_rejected  IN NUMBER,
        p_error_message  IN VARCHAR2
    );

    PROCEDURE log_error(
        p_run_id             IN NUMBER,
        p_pipeline_name      IN VARCHAR2,
        p_source_name        IN VARCHAR2,
        p_source_row_number  IN NUMBER,
        p_error_code         IN VARCHAR2,
        p_error_message      IN VARCHAR2,
        p_raw_record         IN CLOB
    );

    PROCEDURE log_quality_result(
        p_run_id         IN NUMBER,
        p_rule_name      IN VARCHAR2,
        p_table_name     IN VARCHAR2,
        p_column_name    IN VARCHAR2,
        p_result_status  IN VARCHAR2,
        p_checked_rows   IN NUMBER,
        p_failed_rows    IN NUMBER,
        p_details        IN VARCHAR2
    );

END pkg_etl_audit;
/


--PACKAGE BODY
CREATE OR REPLACE PACKAGE BODY etl_control.pkg_etl_audit AS

    PROCEDURE start_run(
        p_pipeline_name IN VARCHAR2,
        p_source_name   IN VARCHAR2,
        p_run_id        OUT NUMBER
    ) AS
    BEGIN
        INSERT INTO etl_control.etl_run (
            pipeline_name,
            source_name,
            start_time,
            status,
            rows_read,
            rows_loaded,
            rows_rejected
        )
        VALUES (
            p_pipeline_name,
            p_source_name,
            SYSTIMESTAMP,
            'RUNNING',
            0,
            0,
            0
        )
        RETURNING run_id INTO p_run_id;

        COMMIT;
    END start_run;


    PROCEDURE finish_run_success(
        p_run_id         IN NUMBER,
        p_rows_read      IN NUMBER,
        p_rows_loaded    IN NUMBER,
        p_rows_rejected  IN NUMBER
    ) AS
    BEGIN
        UPDATE etl_control.etl_run
        SET end_time = SYSTIMESTAMP,
            status = 'SUCCESS',
            rows_read = p_rows_read,
            rows_loaded = p_rows_loaded,
            rows_rejected = p_rows_rejected,
            error_message = NULL
        WHERE run_id = p_run_id;

        COMMIT;
    END finish_run_success;


    PROCEDURE finish_run_failed(
        p_run_id         IN NUMBER,
        p_rows_read      IN NUMBER,
        p_rows_loaded    IN NUMBER,
        p_rows_rejected  IN NUMBER,
        p_error_message  IN VARCHAR2
    ) AS
    BEGIN
        UPDATE etl_control.etl_run
        SET end_time = SYSTIMESTAMP,
            status = 'FAILED',
            rows_read = p_rows_read,
            rows_loaded = p_rows_loaded,
            rows_rejected = p_rows_rejected,
            error_message = SUBSTR(p_error_message, 1, 4000)
        WHERE run_id = p_run_id;

        COMMIT;
    END finish_run_failed;


    PROCEDURE log_error(
        p_run_id             IN NUMBER,
        p_pipeline_name      IN VARCHAR2,
        p_source_name        IN VARCHAR2,
        p_source_row_number  IN NUMBER,
        p_error_code         IN VARCHAR2,
        p_error_message      IN VARCHAR2,
        p_raw_record         IN CLOB
    ) AS
    BEGIN
        INSERT INTO etl_control.etl_error_log (
            run_id,
            pipeline_name,
            source_name,
            source_row_number,
            error_code,
            error_message,
            raw_record,
            created_at
        )
        VALUES (
            p_run_id,
            p_pipeline_name,
            p_source_name,
            p_source_row_number,
            p_error_code,
            SUBSTR(p_error_message, 1, 4000),
            p_raw_record,
            SYSTIMESTAMP
        );

        COMMIT;
    END log_error;


    PROCEDURE log_quality_result(
        p_run_id         IN NUMBER,
        p_rule_name      IN VARCHAR2,
        p_table_name     IN VARCHAR2,
        p_column_name    IN VARCHAR2,
        p_result_status  IN VARCHAR2,
        p_checked_rows   IN NUMBER,
        p_failed_rows    IN NUMBER,
        p_details        IN VARCHAR2
    ) AS
    BEGIN
        INSERT INTO etl_control.data_quality_result (
            run_id,
            rule_name,
            table_name,
            column_name,
            result_status,
            checked_rows,
            failed_rows,
            details,
            checked_at
        )
        VALUES (
            p_run_id,
            p_rule_name,
            p_table_name,
            p_column_name,
            UPPER(p_result_status),
            p_checked_rows,
            p_failed_rows,
            SUBSTR(p_details, 1, 4000),
            SYSTIMESTAMP
        );

        COMMIT;
    END log_quality_result;

END pkg_etl_audit;
/