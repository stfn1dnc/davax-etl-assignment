# DavaX ETL Assignment

## Overview

This repository contains the implementation of the DavaX ETL Data Integration, Modelling and Reporting assignment.

The solution integrates operational employee data from multiple independent systems into a unified analytical model using Oracle Database and PL/SQL.

## Data Sources

- Employee Master Data
- Timesheets
- Absences
- Training Attendance
- DU Exam Schedule

## Architecture

The project follows a layered ETL architecture:

```text
SOURCES
    ↓
STAGING
    ↓
TARGET
```

## Technologies

- Oracle Database Free
- Oracle SQL
- PL/SQL
- Oracle SQL Developer
- Git
- GitHub

## Repository Structure

```text
sql/
docs/
tests/
config/
```
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
python -m venv .venv```

Exemplu de configurare în SQL Developer:

```text
Connection Name: DavaX_SYSTEM
Username: SYSTEM
Password: parola configurată local
Hostname: localhost
Port: 1521
Service name: FREEPDB1
```
Gasiti username urile si parolele in sql/00_setup/001_create_schemas.sql



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

Se deschide SQL Developer.
Se selectează conexiunea SYSTEM.
Conexiunea trebuie să folosească service name-ul FREEPDB1.
Se deschide fișierul:
    sql/99_run_all.sql

SCRIPTUL SE RULEAZA CU F5, NU CTRL + ENTER

## RESET DATABASE

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

SELECT username
FROM dba_users
WHERE username IN (
    'SOURCES',
    'STAGING',
    'TARGET',
    'ETL_CONTROL'
);

Rezultatul așteptat este:

no rows selected