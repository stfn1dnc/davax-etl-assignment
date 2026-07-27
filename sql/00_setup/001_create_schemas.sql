/*
===============================================================================
File:        001_create_schemas.sql
Story:       US-01
Purpose:     Create the Oracle schemas used by the ETL solution.

Execution:
    Run as SYSTEM or another administrative user.
    The connection must use the pluggable database, for example FREEPDB1.
===============================================================================
*/

CREATE USER sources IDENTIFIED BY SourcesLocal123;

CREATE USER staging IDENTIFIED BY StagingLocal123;

CREATE USER target IDENTIFIED BY TargetLocal123;

CREATE USER etl_control IDENTIFIED BY EtlControlLocal123;