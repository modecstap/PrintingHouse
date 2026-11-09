"""Catalog ``take`` protocols backed by SQL."""

import pytest

from backend.new_core.equipment.cutter import CutterID
from backend.new_core.equipment.laminator import LaminatorID
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.personal.cutter_operator import CutterOperatorID
from backend.new_core.personal.laminator_operator import LaminatorOperatorID
from backend.new_core.personal.press_operator import PressOperatorID
from backend.storage.equipment.cutter_repository import SqlCutterRepository
from backend.storage.equipment.laminator_repository import SqlLaminatorRepository
from backend.storage.equipment.printer_repository import SqlPrinterRepository
from backend.storage.personal.cutter_operator_repository import SqlCutterOperatorRepository
from backend.storage.personal.laminator_operator_repository import (
    SqlLaminatorOperatorRepository,
)
from backend.storage.personal.press_operator_repository import SqlPressOperatorRepository
from backend.test.new_core.test_print_run import build_worked_run
from backend.test.storage.catalog_insert import insert_catalogs_from_ctx


def test_catalog_take_round_trips_domain_objects(db_session):
    """Each catalog ``take`` reloads the inserted domain entity."""
    run, *_ , ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    db_session.commit()

    printer = SqlPrinterRepository(db_session).take(PrinterID(1))
    assert printer == next(iter(ctx.printers.values()))

    assert SqlLaminatorRepository(db_session).take(LaminatorID(1)) == next(
        iter(ctx.laminators.values()),
    )
    assert SqlCutterRepository(db_session).take(CutterID(1)) == next(
        iter(ctx.cutters.values()),
    )
    assert SqlPressOperatorRepository(db_session).take(PressOperatorID(1)) == next(
        iter(ctx.press_operators.values()),
    )
    assert SqlLaminatorOperatorRepository(db_session).take(
        LaminatorOperatorID(1),
    ) == next(iter(ctx.laminator_operators.values()))
    assert SqlCutterOperatorRepository(db_session).take(CutterOperatorID(1)) == next(
        iter(ctx.cutter_operators.values()),
    )


def test_catalog_take_missing_raises_key_error(db_session):
    """Unknown catalog ids raise ``KeyError`` like the in-memory dict."""
    with pytest.raises(KeyError):
        SqlPrinterRepository(db_session).take(PrinterID(404))


def test_printer_save_list_delete_round_trip(db_session):
    """``save``, ``take_all``, and ``delete`` change the printer catalog."""
    from decimal import Decimal

    from backend.new_core.equipment.printer import Printer
    from backend.new_core.equipment.printer_repository import PrinterIdOccupied
    from backend.new_core.values.money import Money

    repo = SqlPrinterRepository(db_session)
    printer = Printer(
        id=PrinterID(10),
        startup=Money(Decimal("1")),
        cyan=Money(Decimal("2")),
        magenta=Money(Decimal("3")),
        yellow=Money(Decimal("4")),
        black=Money(Decimal("5")),
    )
    repo.save(printer)
    db_session.commit()
    assert repo.take_all() == (printer,)
    repo.delete(PrinterID(10))
    db_session.commit()
    with pytest.raises(KeyError):
        repo.take(PrinterID(10))

    repo.save(printer)
    db_session.commit()
    with pytest.raises(PrinterIdOccupied):
        repo.save(printer)
