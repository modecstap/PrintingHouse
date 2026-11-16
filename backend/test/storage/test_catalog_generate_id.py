"""Catalog ``generate_id`` backed by PostgreSQL sequences."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import text

from backend.new_core.equipment.printer import Printer, PrinterID, PrinterPrices
from backend.new_core.values.money import Money
from backend.storage.equipment.printer_repository import SqlPrinterRepository
from backend.test.new_core.in_memory_repositories import InMemoryPrinterRepository
from backend.test.new_core.test_print_run import build_worked_run


def test_generate_id_starts_at_zero_and_advances(db_session):
    """Sequence first value is zero and moves independently of saves."""
    repo = SqlPrinterRepository(db_session)
    assert repo.generate_id() == PrinterID(0)
    assert repo.generate_id() == PrinterID(1)


def test_generate_id_follows_max_existing_id(db_session):
    """After setval sync, ``nextval`` returns one past the highest stored id."""
    repo = SqlPrinterRepository(db_session)
    printer = Printer(
        id=PrinterID(10),
        name="№ 10",
        spacing=0,
        prices=PrinterPrices(
            startup=Money(Decimal("1")),
            cyan=Money(Decimal("2")),
            magenta=Money(Decimal("3")),
            yellow=Money(Decimal("4")),
            black=Money(Decimal("5")),
        ),
    )
    repo.save(printer)
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
    """Pre-filled catalog rows do not get duplicated ids from ``generate_id``."""
    _run, *_ , ctx = build_worked_run()
    repo = InMemoryPrinterRepository(items=dict(ctx.printers))
    assert repo.generate_id() == PrinterID(0)


def test_in_memory_generate_id_advances_monotonically():
    repo = InMemoryPrinterRepository()
    assert repo.generate_id() == PrinterID(0)
    assert repo.generate_id() == PrinterID(1)