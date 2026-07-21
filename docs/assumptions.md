# Assumptions

- Employee ID is the business key.
- Oracle Database Free is used as the target database.
- Python is used only for ingestion.
- SQL and PL/SQL perform all transformations.
- Source data is considered immutable.
- Every ETL execution must be auditable.
- Every rejected record must be traceable.