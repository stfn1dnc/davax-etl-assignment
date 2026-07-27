from collections.abc import Generator
from contextlib import contextmanager

import oracledb

from python.common.config import DatabaseConfig


@contextmanager
def get_connection(
    config: DatabaseConfig,
) -> Generator[oracledb.Connection, None, None]:
    connection = None

    try:
        connection = oracledb.connect(
            user=config.user,
            password=config.password,
            dsn=config.dsn,
        )

        yield connection
        connection.commit()

    except oracledb.Error:
        if connection is not None:
            connection.rollback()

        raise

    finally:
        if connection is not None:
            connection.close()