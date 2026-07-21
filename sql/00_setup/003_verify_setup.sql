/*
===============================================================================
File:        003_verify_setup.sql
Story:       US-01
Purpose:     Verify the Oracle schemas and privileges.

Execution:
    Run as SYSTEM.
===============================================================================
*/

SELECT
    username,
    account_status,
    default_tablespace
FROM dba_users
WHERE username IN (
    'SOURCES',
    'STAGING',
    'TARGET',
    'ETL_CONTROL'
)
ORDER BY username;

SELECT
    grantee,
    privilege
FROM dba_sys_privs
WHERE grantee IN (
    'SOURCES',
    'STAGING',
    'TARGET',
    'ETL_CONTROL'
)
ORDER BY grantee, privilege;