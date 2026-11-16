"""Print-run repository persistence against PostgreSQL."""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from backend.new_core.order.order import OrderID
from backend.new_core.print_run.print_run import PrintRun, PrintRunID
from backend.storage.print_run.repository import SqlPrintRunRepository
from backend.storage.print_run.tables import PrintRunRow
from backend.test.new_core.test_print_run import build_worked_run
from backend.test.storage.catalog_insert import (
    insert_catalogs_from_ctx,
    insert_minimal_order_row,
)
from backend.test.storage.helpers import assert_print_run_equal


__all__ = [
    "test_save_all_then_take_all_preserves_order",
    "test_second_save_all_replaces_runs",
    "test_mismatched_for_order_raises_before_persisting",
    "test_generate_id_starts_at_zero",
]

def _repo(db_session: Session) -> SqlPrintRunRepository:
    """Handles repo.

    :param db_session: the db session.

    :return: the SqlPrintRunRepository result.
    """
    return SqlPrintRunRepository(db_session)


def test_save_all_then_take_all_preserves_order(db_session: Session):
    """Tuple order and block graph survive a round trip.

    :param db_session: the db session.
    """
    run, _, _, _, ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    insert_minimal_order_row(db_session, 1)
    repo = _repo(db_session)
    runs = (run,)

    with db_session.begin():
        repo.save_all_for_order(OrderID(1), runs)

    loaded = repo.take_all_for_order(OrderID(1))
    assert len(loaded) == 1
    assert_print_run_equal(loaded[0], run)


def test_second_save_all_replaces_runs(db_session: Session):
    """Second write replaces prior runs for the order.

    :param db_session: the db session.
    """
    run, _, _, _, ctx = build_worked_run(required_count=10)
    insert_catalogs_from_ctx(db_session, ctx)
    insert_minimal_order_row(db_session, 1)
    repo = _repo(db_session)

    with db_session.begin():
        repo.save_all_for_order(OrderID(1), (run,))

    run2, _, _, _, _ = build_worked_run(required_count=20)
    with db_session.begin():
        repo.save_all_for_order(OrderID(1), (run2,))

    loaded = repo.take_all_for_order(OrderID(1))
    assert loaded[0].required_count == 20


def test_mismatched_for_order_raises_before_persisting(db_session: Session):
    """Bad ``for_order`` raises ``ValueError``

    :param db_session: the db session.
    """
    run, _, _, _, ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    insert_minimal_order_row(db_session, 1)
    repo = _repo(db_session)
    bad = PrintRun(
        id=PrintRunID(0),
        for_order=OrderID(2),
        block=run.block,
        required_count=run.required_count,
    )

    with pytest.raises(ValueError, match="for_order 2 != 1"):
        with db_session.begin():
            repo.save_all_for_order(OrderID(1), (bad,))

    count = db_session.execute(
        select(func.count()).select_from(PrintRunRow)).scalar_one()
    assert count == 0


def test_generate_id_starts_at_zero(db_session: Session):
    """Per-order counter returns ``PrintRunID(0)`` first.

    :param db_session: the db session.
    """
    insert_minimal_order_row(db_session, 1)
    repo = _repo(db_session)
    assert repo.generate_id(OrderID(1)) == PrintRunID(0)
    assert repo.generate_id(OrderID(1)) == PrintRunID(1)
