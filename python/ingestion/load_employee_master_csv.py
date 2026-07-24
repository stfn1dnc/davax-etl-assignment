from pathlib import Path
import os

import pandas as pd
import oracledb
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    csv_path = Path("data/generated/employee_master.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Nu există fișierul: {csv_path}")

    df = pd.read_csv(csv_path)

    connection = oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_DSN"),
    )

    rows = [
        (
            row["employee_id"],
            row["employee_name"],
            row["grade"],
            row["discipline"],
            row["line_manager"],
            row["delivery_unit"],
            "VALID",
            None,
            "EMPLOYEE_MASTER",
            csv_path.name,
        )
        for _, row in df.iterrows()
    ]

    sql = """
        INSERT INTO staging.stg_employee (
            employee_id,
            employee_name,
            grade,
            discipline,
            line_manager,
            delivery_unit,
            validation_status,
            validation_message,
            dataset_name,
            source_file_name,
            process_timestamp
        ) VALUES (
            :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, SYSTIMESTAMP
        )
    """

    with connection.cursor() as cursor:
        cursor.executemany(sql, rows)
        connection.commit()

    connection.close()
    print(f"Loaded {len(rows)} rows into staging.stg_employee")


if __name__ == "__main__":
    main()