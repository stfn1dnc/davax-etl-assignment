import logging
from pathlib import Path


def get_logger(
    name: str,
    log_level: str = "INFO",
    log_directory: Path = Path("logs"),
) -> logging.Logger:
    log_directory.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    numeric_level = getattr(
        logging,
        log_level.upper(),
        logging.INFO,
    )

    logger.setLevel(numeric_level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        log_directory / "etl.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger