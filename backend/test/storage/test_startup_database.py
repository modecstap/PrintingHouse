import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from backend.storage.database import Database
from backend.storage.db_config import DBConfig
from backend.storage.tables import (
    OrderCostReportEntity,
    OrderEntity,
    PrintingCostReportEntity,
    PrintingEntity,
)

_PRINTING_SOURCE = (
    Path(__file__).resolve().parents[2] / "storage" / "tables" / "printing.py"
)


def test_printing_id_uses_the_printing_identity() -> None:
    column = PrintingEntity.__table__.c.id
    assert column.identity is not None
    assert column.identity.start == 1
    assert "order_id_seq" not in _PRINTING_SOURCE.read_text(encoding="utf-8")


def test_printing_cost_report_id_uses_its_own_sequence() -> None:
    column = PrintingCostReportEntity.__table__.c.id
    assert str(column.server_default.arg) == "nextval('printing_cost_report_id_seq')"
    assert column.default.name == "printing_cost_report_id_seq"


def test_order_id_keeps_order_id_seq() -> None:
    column = OrderEntity.__table__.c.id
    assert str(column.server_default.arg) == "nextval('order_id_seq')"


def test_order_cost_report_id_keeps_cost_report_id_seq() -> None:
    column = OrderCostReportEntity.__table__.c.id
    assert str(column.server_default.arg) == "nextval('cost_report_id_seq')"


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
