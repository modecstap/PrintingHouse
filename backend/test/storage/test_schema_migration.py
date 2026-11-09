"""Empty schema after Alembic head (session setup in conftest)."""

import pytest

from backend.new_core.order.order import OrderID
from backend.new_core.order.repository import OrderNotFound
from backend.storage.equipment.printer_repository import SqlPrinterRepository
from backend.new_core.equipment.printer import PrinterID
from backend.storage.order.repository import SqlOrderRepository
from backend.storage.print_run.repository import SqlPrintRunRepository
from backend.storage.reference.repository import SqlReferenceRepository


def test_empty_stores_return_protocol_sentinels(db_session):
    """Missing rows yield ``OrderNotFound``, ``KeyError``, or empty tuples."""
    orders = SqlOrderRepository(db_session)
    runs = SqlPrintRunRepository(db_session)
    refs = SqlReferenceRepository(db_session)
    printers = SqlPrinterRepository(db_session)

    with pytest.raises(OrderNotFound, match="take: заказа нет, id=1"):
        orders.take(OrderID(1))

    assert orders.take_latest(5) == ()
    assert orders.take_latest(0) == ()
    assert orders.take_latest(-1) == ()
    assert runs.take_all_for_order(OrderID(1)) == ()
    assert refs.take_all() == ()

    with pytest.raises(KeyError):
        printers.take(PrinterID(1))
