# DavaX ETL Architecture

## Overview

The solution integrates multiple operational data sources into a unified analytical model.

The ETL process is divided into four logical layers.


## Arhitecture

                CSV / Excel Files
                       │
                       ▼
              Python Ingestion Layer
                       │
                       ▼
                SOURCES Schema
                       │
                       ▼
              STAGING Schema
                       │
                       ▼
               TARGET Schema
                       │
                       ▼
                  SQL Reports

                       │
                       ▼

              ETL_CONTROL Schema
          (Audit & Data Quality)


## Layers

### SOURCES

Stores the raw operational data without business transformations.

### STAGING

Standardizes, validates and cleanses the source data.

### TARGET

Contains the analytical Star Schema used for reporting.

### ETL_CONTROL

Stores ETL audit information, execution history and data quality results.

