"""Catalog ``generate_id`` backed by PostgreSQL sequences."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.new_core.equipment.printer import PrinterID
from backend.storage.equipment.printer_repository import SqlPrinterRepository
from backend.test.storage.catalog_insert import insert_printer
from backend.test.storage.helpers import sample_printer
from backend.test.new_core.in_memory_repositories import (
    InMemoryPrinterRepository,
)
from backend.test.new_core.test_print_run import build_worked_run


__all__ = [
    "test_generate_id_starts_at_zero_and_advances",
    "test_generate_id_follows_max_existing_id",
    "test_in_memory_generate_id_skips_prefilled_keys",
    "test_in_memory_generate_id_advances_monotonically",
]

def test_generate_id_starts_at_zero_and_advances(db_session: Session):
    """Sequence first value is zero and moves independently of saves.


    :param db_session: the db session.
    """
    repo = SqlPrinterRepository(db_session)
    assert repo.generate_id() == PrinterID(0)
    assert repo.generate_id() == PrinterID(1)


def test_generate_id_follows_max_existing_id(db_session: Session):
    """After setval sync, ``nextval`` returns one past the highest stored id.

    :param db_session: the db session.
    """
    repo = SqlPrinterRepository(db_session)
    printer = sample_printer(10, "№ 10", 0)
    insert_printer(db_session, printer)
    db_session.commit()
    db_session.execute(
        text(
            "SELECT setval('printer_id_seq', "
            "(SELECT MAX(id) FROM printers), true)"
        ),
    )
    db_session.commit()
    assert repo.generate_id() == PrinterID(11)


def test_in_memory_generate_id_skips_prefilled_keys():
    """Pre-filled catalog rows do not get duplicated ids

    from ``generate_id``.
    """
    _run, _, _, _, ctx = build_worked_run()
    repo = InMemoryPrinterRepository(items=dict(ctx.printers))
    assert repo.generate_id() == PrinterID(0)


def test_in_memory_generate_id_advances_monotonically():
    """Handles test in memory generate id advances monotonically.
    """
    repo = InMemoryPrinterRepository()
    assert repo.generate_id() == PrinterID(0)
    assert repo.generate_id() == PrinterID(1)
