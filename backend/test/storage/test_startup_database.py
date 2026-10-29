import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from backend.storage.database import Database
from backend.storage.db_config import DBConfig
from backend.storage.declarative_base import DeclarativeBase


def test_storage_tables_metadata_contains_only_the_user_table() -> None:
    import backend.storage.tables

    assert set(DeclarativeBase().base.metadata.tables) == {"user"}
    assert backend.storage.tables.UserEntity.__tablename__ == "user"


def test_wait_for_connection_retries_then_opens_without_creating_tables() -> None:
    database = Database(DBConfig.from_env())
    original_engine = database.async_engine
    connection = AsyncMock()
    connection.execute = AsyncMock(side_effect=[ConnectionError("down"), "ok"])
    connect = AsyncMock()
    connect.__aenter__.return_value = connection
    connect.__aexit__.return_value = None
    engine = MagicMock()
    engine.connect.return_value = connect
    database.async_engine = engine
    try:
        with patch("backend.storage.database.time.sleep") as sleep:
            asyncio.run(database.wait_for_connection())
        assert connection.execute.await_count == 2
        for call in connection.execute.await_args_list:
            assert "SELECT 1" in str(call.args[0])
        sleep.assert_called_once_with(10)
        engine.begin.assert_not_called()
    finally:
        database.async_engine = original_engine


def test_main_waits_for_the_database_and_does_not_create_tables() -> None:
    import backend.main as main

    database = Database(DBConfig.from_env())
    assert database.async_engine.pool.checkedout() == 0
    idle_connections = database.async_engine.pool.checkedin()
    called = {"wait": 0, "serve": 0, "create_all": 0}

    async def wait(self) -> None:
        called["wait"] += 1

    async def create_all(self) -> None:
        called["create_all"] += 1

    async def serve(config) -> None:
        called["serve"] += 1

    with (
        patch.object(Database, "wait_for_connection", wait),
        patch.object(Database, "create_all", create_all),
        patch("backend.main.serve", serve),
    ):
        asyncio.run(main.main())
    assert called == {"wait": 1, "serve": 1, "create_all": 0}
    assert database.async_engine.pool.checkedout() == 0
    assert database.async_engine.pool.checkedin() == idle_connections
