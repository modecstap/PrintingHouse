"""PostgreSQL ``PH`` database setup for storage integration tests."""

from __future__ import annotations

from pathlib import Path

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.storage.database import Database
from backend.storage.db_config import DBConfig
from backend.storage.schema import Base

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_ROOT / "storage" / "alembic.ini"

PH_CONFIG = DBConfig(
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432,
    db_name="PH",
)

MAINTENANCE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"


def _recreate_ph_database() -> None:
    with psycopg.connect(MAINTENANCE_URL, autocommit=True) as conn:
        conn.execute('DROP DATABASE IF EXISTS "PH" WITH (FORCE)')
        conn.execute('CREATE DATABASE "PH"')


def _upgrade_head() -> None:
    import os

    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", PH_CONFIG.get_db_url("psycopg"))
    previous_cwd = os.getcwd()
    os.chdir(BACKEND_ROOT.parent)
    try:
        command.upgrade(cfg, "head")
    finally:
        os.chdir(previous_cwd)


def _truncate_all(session: Session) -> None:
    names = ", ".join(
        f'"{table.name}"' for table in reversed(Base.metadata.sorted_tables)
    )
    session.execute(text(f"TRUNCATE {names} RESTART IDENTITY CASCADE"))
    session.execute(text("ALTER SEQUENCE order_id_seq RESTART WITH 0"))
    session.commit()


@pytest.fixture(scope="session")
def ph_database() -> Database:
    """Drops ``PH``, migrates to head, yields a ``Database`` for that catalog."""
    _recreate_ph_database()
    _upgrade_head()
    return Database(PH_CONFIG)


@pytest.fixture
def db_session(ph_database: Database) -> Session:
    """Clean application tables before each test."""
    session = ph_database.session_factory()
    try:
        _truncate_all(session)
        yield session
    finally:
        session.close()
