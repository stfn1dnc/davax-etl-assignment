SET ECHO ON;
SET FEEDBACK ON;
SET SERVEROUTPUT ON;
SET DEFINE OFF;

WHENEVER SQLERROR EXIT SQL.SQLCODE;

PROMPT ============================================================
PROMPT DavaX ETL installation started
PROMPT ============================================================

PROMPT [1/5] Creating schemas...

@@00_setup/001_create_schemas.sql

PROMPT [2/5] Granting permissions...

@@00_setup/002_grant_permissions.sql

PROMPT [3/5] Creating ETL control objects...

@@01_control/001_create_etl_run.sql
@@01_control/002_create_etl_error_log.sql
@@01_control/003_create_data_quality_result.sql
@@01_control/004_create_etl_audit_package.sql

PROMPT [4/5] Creating common target objects...

@@03_target/001_create_dim_date.sql
@@03_target/002_load_dim_date.sql
@@03_target/003_create_dim_activity_type.sql
@@03_target/004_load_dim_activity_type.sql
@@03_target/005_create_fact_employee_activity.sql

PROMPT [5/5] Verifying setup...

@@00_setup/003_verify_setup.sql

PROMPT ============================================================
PROMPT DavaX ETL installation completed successfully
PROMPT ============================================================