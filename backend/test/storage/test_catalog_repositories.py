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
