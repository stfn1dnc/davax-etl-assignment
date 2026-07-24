from pathlib import Path

from python.ingestion.employee_master_loader import (
    build_employee_master,
)

df = build_employee_master(
    Path("data/input")
)

print(df.head())

print()

print(df.shape)