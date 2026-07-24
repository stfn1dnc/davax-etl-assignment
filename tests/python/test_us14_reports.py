import os
from pathlib import Path

import oracledb
from dotenv import load_dotenv


def get_connection():
    load_dotenv()
    return oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_DSN"),
    )


def run_sql_file(connection, file_path, bind_vars=None):
    sql = Path(file_path).read_text(encoding="utf-8")
    with connection.cursor() as cursor:
        cursor.execute(sql, bind_vars or {})
        return cursor.fetchall()


def test_connection_opens():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT USER, SYS_CONTEXT('USERENV', 'CON_NAME') FROM dual"
            )
            user, con_name = cursor.fetchone()

    assert user is not None
    assert con_name is not None


def test_daily_activity_report_runs():
    with get_connection() as connection:
        rows = run_sql_file(
            connection,
            "sql/06_reports/001_daily_employee_activity.sql",
            {"employee_id": "EMP001", "selected_date": "2025-06-24"},
        )
        assert rows is not None


def test_reconciliation_query_runs():
    with get_connection() as connection:
        rows = run_sql_file(
            connection,
            "sql/06_reports/005_source_target_reconciliation.sql",
        )
        assert rows is not None


def test_existing_target_tables_can_be_read():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM target.dim_training")
            dim_training_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM target.fact_employee_activity")
            fact_count = cursor.fetchone()[0]

    assert dim_training_count >= 0
    assert fact_count >= 0