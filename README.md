# DavaX ETL Assignment

## Overview

This repository contains the implementation of the DavaX ETL Data Integration, Modelling and Reporting assignment.

The solution integrates operational employee data from multiple independent systems into a unified analytical model using Oracle Database and PL/SQL.

The project is designed to support traceable ETL processing, SQL-based analysis, and reporting in a layered architecture.

---

## Business Context

DavaX needs a unified view of employee activities by combining information from several independent systems.

The solution supports operational analysis and reporting while keeping the data traceable back to its source.

Available data domains include:

- Timesheets
- Absences
- Training Attendance
- DU Exam Schedule
- Employee Master Data

---

## Functional Requirements

The solution supports:

- querying an employee's activity for a selected date
- producing monthly aggregated reports
- reporting training participation
- reconciliation between source, staging and target
- SQL-friendly access to transformed data

---

## Technical Requirements

The implementation follows these technical principles:

- layered architecture with source, staging and target schemas
- ingestion metadata such as `dataset_name` and `process_timestamp`
- star schema modelling in the analytical layer
- extendable design for future data sources
- SQL scripts for creation, loading, validation and reporting
- Python scripts for helper processing and file generation

---

## Architecture

### ETL Arhitecture

The project follows a layered ETL architecture:

```text
SOURCES
    ↓
STAGING
    ↓
TARGET
    ↓
ETL_CONTROL
```
## Main Flow

CSV / source files
        →
Python parsing / generation
        →
SOURCE raw tables
        →
STAGING validation and standardization
        →
TARGET star schema
        →
SQL reports and reconciliation checks

## Data Sources
- Employee Master Data
- Timesheets
- Absences
- Training Attendance
- DU Exam Schedule


## Technologies

- Oracle Database Free
- Oracle SQL
- PL/SQL
- Oracle SQL Developer
- Git
- GitHub
- Python 3.10 or newer

## Repository Structure

```text
sql/
docs/
tests/
config/
data/
python/
README.md
requirements.txt
```
## Main folders

- sql/ – setup, source, staging, target, load, quality and report scripts
- docs/ – architecture, assumptions, mapping and ERD
- tests/ – Python and SQL tests
- config/ – configuration files
- data/input/ – local input files
- data/generated/ – generated intermediate files
- data/processed/ – processed files
- data/rejected/ – rejected files
- python/ – parsing, ingestion and helper scripts

## Prerequisites

Pentru rularea proiectului sunt necesare următoarele aplicații:

- Git;
- Python 3.10 sau o versiune mai nouă;
- Oracle Database Free;
- Oracle SQL Developer;
- Visual Studio Code sau un alt editor de cod;
- acces la terminal, PowerShell sau Git Bash.

## Python setup

După clonarea repository-ului, se recomandă crearea unui mediu virtual Python.

Din directorul principal al proiectului se rulează:

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

python -m pip install -r requirements.txt
```

Gasiti username urile si parolele in sql/00_setup/001_create_schemas.sql

## Oracle Connection Example
Exemplu de configurare în SQL Developer:

Connection Name: DavaX_SYSTEM
Username: SYSTEM
Password: parola configurată local
Hostname: localhost
Port: 1521
Service name: FREEPDB1

Găsiți username-urile și parolele în sql/00_setup/001_create_schemas.sql.

## How to Run

### 99_run_all.sql 
instalează obiectele proiectului în ordinea corectă.

Acesta creează:

schemele Oracle;
permisiunile necesare;
tabelele de audit;
package-ul PL/SQL pentru audit;
dimensiunile comune;
tabela de activități;
datele inițiale din dimensiuni;
verificările finale.

Pentru rulare:

1. Se deschide SQL Developer.
2. Se selectează conexiunea SYSTEM.
3. Conexiunea trebuie să folosească service name-ul FREEPDB1.
4. Se deschide fișierul:
    ```text
    sql/99_run_all.sql

SCRIPTUL SE RULEAZA CU F5, NU CTRL + ENTER

## Reset Database

Resetarea bazei de date șterge toate schemele și obiectele create pentru proiect.

Resetul trebuie folosit înainte de testarea unei instalări complete de la zero.

Fișierul folosit este:

sql/00_setup/099_reset_database.sql

Pentru rulare:

Se deschide SQL Developer.
Se selectează conexiunea SYSTEM.
Se deschide scriptul de reset.
Se rulează cu F5.

Scriptul șterge următoarele scheme:

SOURCES
STAGING
TARGET
ETL_CONTROL

Toate tabelele, package-urile, secvențele și celelalte obiecte deținute de aceste scheme vor fi șterse.

După reset se verifică rezultatul cu:

``` sql
SELECT username
FROM dba_users
WHERE username IN (
    'SOURCES',
    'STAGING',
    'TARGET',
    'ETL_CONTROL'
);
```

Rezultatul așteptat este:

no rows selected

## Star Schema
Analytical model is implemented as a star schema.

### Dimensions
- DIM_EMPLOYEE
- DIM_PROJECT
- DIM_DATE
- DIM_ACTIVITY_TYPE
- DIM_TRAINING
### Fact
- FACT_EMPLOYEE_ACTIVITY
### ERD
The star schema diagram is available in:

docs/erd/star_schema.png

## Reports and Validation

The reporting layer contains SQL queries for:

- daily employee activity
- monthly employee activity
- training participation
- employees without activity
- source / target reconciliation

Validation checks include:

- source vs staging counts
- staging validation statuses
- target fact row checks
- report execution tests

Example checks:

```sql 
SELECT COUNT(*) FROM sources.training_session_raw;

SELECT COUNT(*) FROM staging.stg_training_session;

SELECT COUNT(*) FROM target.fact_employee_activity;
```

## Assumptions

The project uses the following assumptions:

- employee_id is used as the business key for matching employee records
- UNKNOWN rows are used as fallback seed records in dimensions
- some business attributes are historical where required
- some reports depend on dimensions owned by other user stories
- local input files are the canonical source for Python generation scripts
- data in data/generated/ is treated as an intermediate artefact
- validation and reconciliation are performed using SQL queries and test scripts

## Documentation

Additional documentation is available in docs/:

- architecture.md
- assumptions.md
- source_to_target_mapping.md
- naming_conventions.md
- erd/star_schema.png

## SQL Folder Layout

### sql/00_setup/

- Database setup scripts
- Schema creation
- permissions.

### sql/01_control/

- ETL control tables
- audit tables 
- logging 
- helper packages.

### sql/01_sources/

- Raw source table creation scripts.

### sql/02_sources/

- Additional source objects for domain-specific inputs.

### sql/02_staging/

- Staging table creation
- staging logic.

### sql/03_target/

- Target dimension 
- fact table creation scripts.

### sql/04_load/

- Load and merge scripts that move data from staging into target.

### sql/05_quality/

- Validation and reconciliation scripts.

#### sql/06_reports/

- Reporting queries for daily, monthly and reconciliation outputs.

### sql/07_test_data/

- Optional sample test data scripts.

### sql/99_run_all.sql

- Convenience script that runs the full setup / load sequence.

## Python Folder Layout

### python/common/

Common helper utilities for 
- configuration
- file operations
- logging 
- DB access.

### python/ingestion/

Scripts for 
- ingestion
- file processing 
- employee master generation/loading.

### python/training_attendance/

- Training attendance parsing and loading logic.

### python/timesheet_absences/

- Timesheet absence processing logic.

### python/exam_absences/

- Exam / absence schedule processing logic.

### python/validation/

- Validation helpers and checks.

### python/utils/

- Shared utility code.

### python/main.py

- Project entry point if a combined run is needed.

## Summary

The DavaX ETL solution provides a structured and extensible architecture for integrating employee-related operational datasets into a centralized analytical model.

Using Oracle Database, PL/SQL, Python ingestion processes, validation controls, auditing mechanisms, and dimensional modelling, the Platform delivers reliable reporting capabilities while maintaining full traceability from source systems to analytical outputs.