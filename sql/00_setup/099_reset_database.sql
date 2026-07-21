/*
===============================================================================
File:        099_reset_database.sql
Story:       US-01
Purpose:     Remove all project schemas in a development environment.

WARNING:
    This script deletes all project schemas, objects and data.
    Run only in local development or test environments.
===============================================================================
*/

DROP USER target CASCADE;
DROP USER staging CASCADE;
DROP USER sources CASCADE;
DROP USER etl_control CASCADE;