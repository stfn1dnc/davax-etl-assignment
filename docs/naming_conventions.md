# Naming Conventions

## Oracle Schemas

SOURCES
STAGING
TARGET
ETL_CONTROL

---

## Tables

Raw tables

ENTITY_RAW

Example

EMPLOYEE_RAW

---

Staging tables

STG_ENTITY

Example

STG_EMPLOYEE

---

Dimensions

DIM_ENTITY

Example

DIM_EMPLOYEE

---

Fact tables

FACT_ENTITY

Example

FACT_EMPLOYEE_ACTIVITY

---

## Sequences

SEQ_TABLE_NAME

Example

SEQ_DIM_EMPLOYEE

---

## Packages

PKG_PURPOSE

Example

PKG_ETL_AUDIT

---

## Views

VW_ENTITY

---

## Materialized Views

MV_ENTITY

---

## Python

snake_case

---

## Git

feature/US-XX-description

bugfix/US-XX-description

---

## Commit Messages

[US-01] Create Oracle Schemas

[US-02] Create Audit Tables