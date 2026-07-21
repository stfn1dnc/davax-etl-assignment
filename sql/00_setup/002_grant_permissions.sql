/*
===============================================================================
File:        002_grant_permissions.sql
Story:       US-01
Purpose:     Grant the required privileges to the ETL schemas.

Execution:
    Run as SYSTEM after 001_create_schemas.sql.
===============================================================================
*/

GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE
TO sources;

GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW,
      CREATE SEQUENCE, CREATE PROCEDURE
TO staging;

GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW,
      CREATE MATERIALIZED VIEW, CREATE SEQUENCE,
      CREATE PROCEDURE
TO target;

GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE,
      CREATE PROCEDURE
TO etl_control;

ALTER USER sources QUOTA UNLIMITED ON users;
ALTER USER staging QUOTA UNLIMITED ON users;
ALTER USER target QUOTA UNLIMITED ON users;
ALTER USER etl_control QUOTA UNLIMITED ON users;