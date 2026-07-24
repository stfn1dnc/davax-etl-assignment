from typing import Any

from python.common.config import get_config
from python.common.db_connection import get_connection
from python.ingestion.file_reader import read_file


class WorkedHoursLoader:
    """Loads worked-hours CSV files into SOURCES.WORKED_HOURS_RAW."""

    PIPELINE_NAME = "WORKED_HOURS_PIPELINE"
    DATASET_NAME = "WORKED_HOURS"
    SOURCE_FILE_NAME = "Timesheet__WorkedHours.csv"

    def __init__(self) -> None:
        self.config = get_config(require_database_credentials=True)

    @staticmethod
    def validate_columns(df: Any) -> None:
        required_columns = {
            "Name",
            "Email",
            "DateWorked",
            "WorkedHours",
            "ProjectCode",
        }

        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(
                f"Missing required CSV columns: {missing}"
            )

    @staticmethod
    def validate_rows(df: Any) -> None:
        required_value_columns = {
            "Name",
            "Email",
            "DateWorked",
            "WorkedHours",
            "ProjectCode",
        }

        for column in required_value_columns:
            if df[column].isna().any():
                raise ValueError(
                    f"Column '{column}' contains empty values."
                )

        if (df["WorkedHours"] < 0).any():
            raise ValueError(
                "Column 'WorkedHours' contains negative values."
            )

    def start_run(
        self,
        cursor: Any,
        source_file_name: str,
    ) -> int:
        run_id_variable = cursor.var(int)

        cursor.callproc(
            "ETL_CONTROL.PKG_ETL_AUDIT.START_RUN",
            [
                self.PIPELINE_NAME,
                source_file_name,
                run_id_variable,
            ],
        )

        run_id = run_id_variable.getvalue()

        if run_id is None:
            raise RuntimeError(
                "START_RUN did not return a run ID."
            )

        return int(run_id)

    def prepare_rows(
        self,
        df: Any,
        run_id: int,
        source_file_name: str,
    ) -> list[tuple]:
        rows = []

        for source_row_number, row in enumerate(
            df.itertuples(index=False),
            start=2,
        ):
            rows.append(
                (
                    run_id,
                    self.DATASET_NAME,
                    source_file_name,
                    source_row_number,
                    str(row.Name).strip(),
                    str(row.Email).strip(),
                    str(row.DateWorked).strip(),
                    float(row.WorkedHours),
                    str(row.ProjectCode).strip(),
                )
            )

        return rows

    @staticmethod
    def insert_rows(
        cursor: Any,
        rows: list[tuple],
    ) -> int:
        if not rows:
            return 0

        insert_sql = """
            INSERT INTO worked_hours_raw (
                run_id,
                dataset_name,
                source_file_name,
                source_row_number,
                name_raw,
                email_raw,
                date_worked_raw,
                worked_hours_raw,
                project_code_raw
            )
            VALUES (
                :1,
                :2,
                :3,
                :4,
                :5,
                :6,
                :7,
                :8,
                :9
            )
        """

        cursor.executemany(insert_sql, rows)

        return cursor.rowcount

    @staticmethod
    def finish_run_success(
        cursor: Any,
        run_id: int,
        rows_read: int,
        rows_loaded: int,
        rows_rejected: int = 0,
    ) -> None:
        cursor.callproc(
            "ETL_CONTROL.PKG_ETL_AUDIT.FINISH_RUN_SUCCESS",
            [
                run_id,
                rows_read,
                rows_loaded,
                rows_rejected,
            ],
        )

    @staticmethod
    def log_error(
        cursor: Any,
        run_id: int,
        source_file_name: str,
        error_message: str,
    ) -> None:
        cursor.callproc(
            "ETL_CONTROL.PKG_ETL_AUDIT.LOG_ERROR",
            [
                run_id,
                WorkedHoursLoader.PIPELINE_NAME,
                source_file_name,
                None,
                "WORKED_HOURS_LOAD_ERROR",
                error_message[:4000],
                None,
            ],
        )

    @staticmethod
    def finish_run_failed(
        cursor: Any,
        run_id: int,
        rows_read: int,
        rows_loaded: int,
        rows_rejected: int,
        error_message: str,
    ) -> None:
        cursor.callproc(
            "ETL_CONTROL.PKG_ETL_AUDIT.FINISH_RUN_FAILED",
            [
                run_id,
                rows_read,
                rows_loaded,
                rows_rejected,
                error_message[:4000],
            ],
        )

    def load(self) -> None:
        input_file = (
            self.config.input_data_path
            / self.SOURCE_FILE_NAME
        )

        if not input_file.exists():
            raise FileNotFoundError(
                f"Input file does not exist: {input_file.resolve()}"
            )

        df = read_file(input_file)

        self.validate_columns(df)
        self.validate_rows(df)

        rows_read = len(df)
        rows_loaded = 0
        run_id = None

        with get_connection(self.config.database) as connection:
            with connection.cursor() as cursor:
                run_id = self.start_run(
                    cursor=cursor,
                    source_file_name=input_file.name,
                )

                try:
                    rows = self.prepare_rows(
                        df=df,
                        run_id=run_id,
                        source_file_name=input_file.name,
                    )

                    rows_loaded = self.insert_rows(
                        cursor=cursor,
                        rows=rows,
                    )

                    self.finish_run_success(
                        cursor=cursor,
                        run_id=run_id,
                        rows_read=rows_read,
                        rows_loaded=rows_loaded,
                        rows_rejected=0,
                    )

                except Exception as error:
                    error_message = str(error)
                    rows_rejected = max(
                        rows_read - rows_loaded,
                        0,
                    )

                    try:
                        self.log_error(
                            cursor=cursor,
                            run_id=run_id,
                            source_file_name=input_file.name,
                            error_message=error_message,
                        )

                        self.finish_run_failed(
                            cursor=cursor,
                            run_id=run_id,
                            rows_read=rows_read,
                            rows_loaded=rows_loaded,
                            rows_rejected=rows_rejected,
                            error_message=error_message,
                        )

                    except Exception:
                        pass

                    raise

        print(f"Run ID: {run_id}")
        print(f"Rows read: {rows_read}")
        print(f"Rows loaded: {rows_loaded}")
        print("Worked-hours ingestion completed successfully.")


def main() -> None:
    loader = WorkedHoursLoader()
    loader.load()


if __name__ == "__main__":
    main()