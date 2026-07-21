from python.common.config import get_config
from python.common.file_utils import find_input_files
from python.common.logger import get_logger
from python.ingestion.file_reader import read_file

def main() -> None:
    config = get_config()

    logger = get_logger(
        name="davax_etl",
        log_level=config.log_level,
        log_directory=config.log_path,
    )

    logger.info("ETL application started.")

    input_files = find_input_files(config.input_data_path)

    if not input_files:
        logger.warning(
            "No input files were found in %s.",
            config.input_data_path,
        )
    else:
        for input_file in input_files:
            logger.info(
                "Detected input file: %s",
                input_file,
            )
            try:
                dataframe = read_file(input_file)

                logger.info(
                    "File %s contains %s rows and %s columns.",
                    input_file.name,
                    len(dataframe),
                    len(dataframe.columns),
                )

                logger.info(
                    "Columns in %s: %s",
                    input_file.name,
                    list(dataframe.columns),
                )

                print("\n")
                print("=" * 60)
                print(f"File: {input_file.name}")
                print(f"Rows: {len(dataframe)}")
                print(f"Columns: {len(dataframe.columns)}")
                print("Column names:")
                print(list(dataframe.columns))
                print("\nFirst 5 rows:")
                print(dataframe.head())
                print("=" * 60)

            except Exception as error:
                logger.error(
                    "Could not read file %s. Error: %s",
                    input_file.name,
                    error,
                )
    logger.info("ETL application finished.")


if __name__ == "__main__":
    main()