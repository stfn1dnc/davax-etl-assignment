from python.ingestion.employee_master_builder import (
    build_employee_master,
)

df = build_employee_master()

print(df.head())
print()
print(df.shape)