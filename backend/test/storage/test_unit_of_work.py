"""Order unit of work transaction boundaries."""

import pytest
from sqlalchemy.orm import Session

from backend.new_core.order.order import OrderContent, OrderID
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.order.repository import OrderNotFound
from backend.storage.order.unit_of_work import SqlOrderUnitOfWork
from backend.test.new_core.test_print_run import build_worked_run
from backend.test.storage.catalog_insert import insert_catalogs_from_ctx
from backend.test.storage.helpers import make_order, product_from_run


__all__ = [
    "test_transaction_rolls_back_orders_and_print_runs",
    "test_transaction_commits_orders_and_print_runs",
    "test_rollback_does_not_rewind_order_id_sequence",
]

def _run_for_order(run: PrintRun, order_id: OrderID) -> PrintRun:
    """Handles run for order.

    :param run: the run.
    :param order_id: id of the order.

    :return: the PrintRun result.
    """
    return PrintRun(run.id, order_id, run.block, run.required_count)


def test_transaction_rolls_back_orders_and_print_runs(db_session: Session):
    """Any exception empties both stores.

    :param db_session: the db session.

    :raises RuntimeError: when the operation fails.
    """
    run, _, _, _, ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    uow = SqlOrderUnitOfWork(db_session)
    order = make_order(4, OrderContent(product=product_from_run(run), count=2))
    stored_run = _run_for_order(run, order.id)

    def work() -> None:
        """Handles work.

        :raises RuntimeError: when the operation fails.
        """
        uow.orders.save(order)
        uow.print_runs.save_all_for_order(order.id, (stored_run,))
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        uow.transaction(work)

    with pytest.raises(OrderNotFound):
        uow.orders.take(order.id)
    assert not uow.print_runs.take_all_for_order(order.id)


def test_transaction_commits_orders_and_print_runs(db_session: Session):
    """Successful work persists both repositories.

    :param db_session: the db session.
    """
    run, _, _, _, ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    uow = SqlOrderUnitOfWork(db_session)
    order = make_order(8, OrderContent(product=product_from_run(run), count=2))
    stored_run = _run_for_order(run, order.id)

    def work() -> None:
        """Handles work.
        """
        uow.orders.save(order)
        uow.print_runs.save_all_for_order(order.id, (stored_run,))

    uow.transaction(work)

    assert uow.orders.take(order.id) == order
    assert len(uow.print_runs.take_all_for_order(order.id)) == 1


def test_rollback_does_not_rewind_order_id_sequence(db_session: Session):
    """``order_id_seq`` keeps advancing after a rolled-back save attempt.

    :param db_session: the db session.

    :raises RuntimeError: when the operation fails.
    """
    run, _, _, _, ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    uow = SqlOrderUnitOfWork(db_session)
    order = make_order(0, OrderContent(product=product_from_run(run), count=1))

    assert uow.orders.generate_id() == OrderID(0)
    db_session.commit()

    def work() -> None:
        """Handles work.

        :raises RuntimeError: when the operation fails.
        """
        uow.orders.save(order)
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        uow.transaction(work)

    assert uow.orders.generate_id() == OrderID(1)
