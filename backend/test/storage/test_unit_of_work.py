"""Order unit of work transaction boundaries."""

import pytest

from backend.new_core import Order
from backend.new_core.order.order import OrderID
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.order.repository import OrderNotFound
from backend.storage.order.unit_of_work import SqlOrderUnitOfWork
from backend.test.new_core.test_print_run import build_worked_run
from backend.test.storage.catalog_insert import insert_catalogs_from_ctx
from backend.test.storage.helpers import product_from_run


def _run_for_order(run: PrintRun, order_id: OrderID) -> PrintRun:
    return PrintRun(run.id, order_id, run.block, run.required_count)


def test_transaction_rolls_back_orders_and_print_runs(db_session):
    """Any exception empties both stores."""
    run, *_ , ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    uow = SqlOrderUnitOfWork(db_session)
    order = Order(id=OrderID(4), product=product_from_run(run), count=2)
    stored_run = _run_for_order(run, order.id)

    def work() -> None:
        uow.orders.save(order)
        uow.print_runs.save_all_for_order(order.id, (stored_run,))
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        uow.transaction(work)

    with pytest.raises(OrderNotFound):
        uow.orders.take(order.id)
    assert uow.print_runs.take_all_for_order(order.id) == ()


def test_transaction_commits_orders_and_print_runs(db_session):
    """Successful work persists both repositories."""
    run, *_ , ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    uow = SqlOrderUnitOfWork(db_session)
    order = Order(id=OrderID(8), product=product_from_run(run), count=2)
    stored_run = _run_for_order(run, order.id)

    def work() -> None:
        uow.orders.save(order)
        uow.print_runs.save_all_for_order(order.id, (stored_run,))

    uow.transaction(work)

    assert uow.orders.take(order.id) == order
    assert len(uow.print_runs.take_all_for_order(order.id)) == 1


def test_rollback_does_not_rewind_order_id_sequence(db_session):
    """``order_id_seq`` keeps advancing after a rolled-back save attempt."""
    run, *_ , ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    uow = SqlOrderUnitOfWork(db_session)
    order = Order(id=OrderID(0), product=product_from_run(run), count=1)

    assert uow.orders.generate_id() == OrderID(0)
    db_session.commit()

    def work() -> None:
        uow.orders.save(order)
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        uow.transaction(work)

    assert uow.orders.generate_id() == OrderID(1)
