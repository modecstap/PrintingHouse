"""Sync SQLAlchemy engine and connection wait loop."""

from __future__ import annotations

import asyncio

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.storage.db_config import DBConfig


class Database:
    """Holds a sync engine and session factory for one ``DBConfig``."""

    def __init__(self, config: DBConfig) -> None:
        """Creates the engine and session maker for ``config``.

        :param config: database host and credentials.
        """
        self._config = config
        self.engine: Engine = create_engine(config.get_db_url("psycopg"))
        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    def _ping(self) -> None:
        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    async def wait_for_connection(self) -> None:
        """Retries until ``SELECT 1`` succeeds on a sync connection.

        Uses ``asyncio.to_thread`` for the blocking probe and waits one second
        between failures. Does not log credentials or connection URLs.
        """
        while True:
            try:
                await asyncio.to_thread(self._ping)
                return
            except Exception:
                await asyncio.sleep(1)
