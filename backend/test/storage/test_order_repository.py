"""Order repository persistence against PostgreSQL."""

import pytest
from sqlalchemy.exc import IntegrityError

from backend.new_core import Order
from backend.new_core.order.order import OrderID
from backend.new_core.order.repository import OrderIdOccupied, OrderNotFound
from backend.storage.order.repository import SqlOrderRepository
from backend.test.new_core.test_print_run import build_worked_run
from backend.test.storage.catalog_insert import insert_catalogs_from_ctx
from backend.test.storage.helpers import product_from_run


def test_save_then_take_round_trips_full_graph(db_session):
    """Insert-only save reloads nested parts, operations, and additional works."""
    run, *_ , ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    repo = SqlOrderRepository(db_session)
    order = Order(id=OrderID(5), product=product_from_run(run), count=4)

    with db_session.begin():
        repo.save(order)

    loaded = repo.take(OrderID(5))
    assert loaded == order


def test_save_print_only_graph_round_trips(db_session):
    """A print-only block still round-trips."""
    run, *_ , ctx = build_worked_run(with_laminate=False, with_cut=False)
    insert_catalogs_from_ctx(db_session, ctx)
    repo = SqlOrderRepository(db_session)
    order = Order(id=OrderID(2), product=product_from_run(run), count=1)

    with db_session.begin():
        repo.save(order)

    assert repo.take(OrderID(2)) == order


def test_second_save_same_id_raises_order_id_occupied(db_session):
    """Duplicate id becomes ``OrderIdOccupied`` with Russian text."""
    run, *_ , ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    repo = SqlOrderRepository(db_session)
    order = Order(id=OrderID(7), product=product_from_run(run), count=1)

    with db_session.begin():
        repo.save(order)

    with pytest.raises(OrderIdOccupied, match="save: заказ уже есть, id=7"):
        with db_session.begin():
            repo.save(order)


def test_take_missing_raises_order_not_found(db_session):
    """Missing id uses ``take: заказа нет``."""
    repo = SqlOrderRepository(db_session)
    with pytest.raises(OrderNotFound, match="take: заказа нет, id=99"):
        repo.take(OrderID(99))


def test_generate_id_starts_at_zero_and_advances(db_session):
    """Sequence first value is zero and moves independently of saves."""
    repo = SqlOrderRepository(db_session)
    assert repo.generate_id() == OrderID(0)

    run, *_ , ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    with db_session.begin():
        repo.save(Order(id=OrderID(0), product=product_from_run(run), count=1))

    assert repo.generate_id() == OrderID(1)


def test_save_with_unknown_printer_raises_integrity_error(db_session):
    """Catalog FK violations stay ``IntegrityError``."""
    run, *_ , _ctx = build_worked_run()
    repo = SqlOrderRepository(db_session)
    order = Order(id=OrderID(3), product=product_from_run(run), count=1)

    with pytest.raises(IntegrityError):
        with db_session.begin():
            repo.save(order)


def test_take_latest_orders_by_descending_id(db_session):
    """``take_latest`` returns the highest ids first."""
    run, *_ , ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    repo = SqlOrderRepository(db_session)
    with db_session.begin():
        repo.save(Order(id=OrderID(1), product=product_from_run(run), count=1))
        repo.save(Order(id=OrderID(10), product=product_from_run(run), count=2))

    latest = repo.take_latest(2)
    assert [order.id.value for order in latest] == [10, 1]
