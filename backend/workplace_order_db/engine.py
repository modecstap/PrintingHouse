from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from backend.storage.db_config import DBConfig


def create_sync_engine() -> Engine:
    """Создаёт новый синхронный Engine из DB_*.

    Результат: Engine на postgresql+psycopg. Не singleton.
    Побочные эффекты: читает DB_USER, DB_PASSWORD, DB_HOST,
    DB_PORT и DB_NAME через DBConfig.from_env.
    """
    url = DBConfig.from_env().get_db_url("psycopg")
    return create_engine(url)
