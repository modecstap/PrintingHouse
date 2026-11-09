"""Database bootstrap wait loop against local ``PH``."""

import asyncio

from backend.storage.database import Database
from backend.test.storage.conftest import PH_CONFIG


def test_wait_for_connection_succeeds_on_ph():
    """``wait_for_connection`` completes when Postgres accepts ``SELECT 1``."""
    asyncio.run(Database(PH_CONFIG).wait_for_connection())
