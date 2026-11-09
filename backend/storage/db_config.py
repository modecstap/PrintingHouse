"""PostgreSQL connection settings from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DBConfig:
    """Host, credentials, and database name for SQLAlchemy URLs."""

    user: str
    password: str | None
    host: str
    port: int
    db_name: str

    @classmethod
    def from_env(cls) -> DBConfig:
        """Builds config from ``DB_*`` variables and documented defaults.

        :return: connection settings for the application database.
        """
        return cls(
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", "postgres"),
        )

    def get_db_url(self, driver: str) -> str:
        """Returns a SQLAlchemy URL for the given DBAPI driver name.

        :param driver: sync driver segment, e.g. ``psycopg``.

        :return: ``postgresql+{driver}://…`` URL.
        """
        if self.password:
            auth = f"{self.user}:{self.password}"
        else:
            auth = self.user
        return (
            f"postgresql+{driver}://{auth}@{self.host}:{self.port}/{self.db_name}"
        )
