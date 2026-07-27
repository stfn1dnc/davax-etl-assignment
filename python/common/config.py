from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

"""load date din fisierul env"""
load_dotenv()

"""gruparea setarilor bazei de date, 
DSN este adresa folosita pentru conectarea la baza de date"""
@dataclass(frozen=True)
class DatabaseConfig:
    user: str
    password: str
    host: str
    port: int
    service_name: str

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}/{self.service_name}"



"""Gruparea configuratiilor aplicatiei"""
@dataclass(frozen=True)
class ApplicationConfig:
    database: DatabaseConfig
    log_level: str
    input_data_path: Path
    rejected_data_path: Path
    log_path: Path


def get_config(require_database_credentials: bool = False) -> ApplicationConfig:
    db_user = os.getenv("DB_USER", "")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port_raw = os.getenv("DB_PORT", "1521")
    db_service_name = os.getenv("DB_SERVICE_NAME", "FREEPDB1")

##validare port
 
    if db_port_raw:
            db_port = int(db_port_raw)
    else:
            db_port = 1521
    

    if require_database_credentials and (not db_user or not db_password):
        raise ValueError(
            "DB_USER and DB_PASSWORD must be configured in the .env file."
        )

    return ApplicationConfig(
        database=DatabaseConfig(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            service_name=db_service_name,
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        input_data_path=Path(os.getenv("INPUT_DATA_PATH", "data/input")),
        rejected_data_path=Path(
            os.getenv("REJECTED_DATA_PATH", "data/rejected")
        ),
        log_path=Path(os.getenv("LOG_PATH", "logs")),
    )