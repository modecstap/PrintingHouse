from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from backend.storage.db_config import DBConfig


def create_sync_engine() -> Engine:
    """Creates a new synchronous Engine from DB_*.

    :return: an Engine on postgresql+psycopg. It is not a singleton.
    """
    url = DBConfig.from_env().get_db_url("psycopg")
    return create_engine(url)
