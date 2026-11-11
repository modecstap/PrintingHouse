"""Catalog ``take`` protocols backed by SQL."""

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from backend.new_core.equipment.cutter import CutterID
from backend.new_core.equipment.laminator import LaminatorID
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.format import Format
from backend.new_core.materials.film import Film, FilmID
from backend.new_core.materials.paper import Paper
from backend.new_core.materials.sheet import Sheet, SheetID
from backend.new_core.personal.cutter_operator import CutterOperatorID
from backend.new_core.personal.laminator_operator import LaminatorOperatorID
from backend.new_core.personal.press_operator import PressOperatorID
from backend.storage.equipment.cutter_repository import SqlCutterRepository
from backend.storage.equipment.laminator_repository import SqlLaminatorRepository
from backend.storage.equipment.printer_repository import SqlPrinterRepository
from backend.storage.materials.film_repository import SqlFilmRepository
from backend.storage.materials.sheet_repository import SqlSheetRepository
from backend.storage.part.tables import PartLaminateRow, PartOperationRow, PartRow
from backend.storage.personal.cutter_operator_repository import SqlCutterOperatorRepository
from backend.storage.personal.laminator_operator_repository import (
    SqlLaminatorOperatorRepository,
)
from backend.storage.personal.press_operator_repository import SqlPressOperatorRepository
from backend.test.new_core.test_print_run import build_worked_run
from backend.new_core.values.money import Money
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


def test_film_add_take_all_replace_take_round_trip(db_session):
    """``add``, ``take_all``, ``replace``, and ``take`` round-trip a film."""
    repo = SqlFilmRepository(db_session)
    price = Money(Decimal("1.25"))
    first_id = repo.add("dup", price, 50)
    second_id = repo.add("dup", price, 50)
    db_session.commit()
    assert first_id != second_id
    assert len(repo.take_all()) == 2

    updated = Film(
        id=first_id,
        name="renamed",
        price=Money(Decimal("2")),
        density=60,
    )
    repo.replace(updated)
    db_session.commit()
    assert repo.take(first_id) == updated


def test_sheet_add_take_all_replace_take_round_trip(db_session):
    """``add``, ``take_all``, ``replace``, and ``take`` round-trip a sheet."""
    repo = SqlSheetRepository(db_session)
    paper = Paper(
        density=100,
        thickness=Decimal(1),
        name="dup",
        price_per_kilo=Money(Decimal("10")),
    )
    fmt = Format(name="SRA3", height=450, width=320)
    first_id = repo.add(paper, fmt)
    second_id = repo.add(paper, fmt)
    db_session.commit()
    assert first_id != second_id
    assert len(repo.take_all()) == 2

    updated = Sheet(
        id=first_id,
        paper=Paper(
            density=120,
            thickness=Decimal(2),
            name="new",
            price_per_kilo=Money(Decimal("12")),
        ),
        format=Format(name="A2", height=594, width=420),
    )
    repo.replace(updated)
    db_session.commit()
    assert repo.take(first_id) == updated


def test_sheet_round_trip_fractional_thickness(db_session):
    """Fractional and whole thickness values round-trip through storage."""
    repo = SqlSheetRepository(db_session)
    fractional = Paper(
        density=80,
        thickness=Decimal("0.15"),
        name="тонкая",
        price_per_kilo=Money(Decimal("10")),
    )
    fmt = Format(name="SRA3", height=450, width=320)
    sheet_id = repo.add(fractional, fmt)
    db_session.commit()
    loaded = repo.take(sheet_id)
    assert loaded.paper.thickness == Decimal("0.15")

    whole_id = repo.add(
        Paper(100, Decimal(1), "целая", Money(Decimal("5"))),
        fmt,
    )
    db_session.commit()
    whole = repo.take(whole_id)
    assert whole.paper.thickness.quantize(Decimal("0.01")) == Decimal("1.00")


@pytest.mark.parametrize(
    ("repo_factory", "missing_id"),
    [
        (lambda session: SqlFilmRepository(session), FilmID(404)),
        (lambda session: SqlSheetRepository(session), SheetID(404)),
    ],
)
def test_material_catalog_take_missing_raises_key_error(db_session, repo_factory, missing_id):
    """Unknown film or sheet ids raise ``KeyError``."""
    repo = repo_factory(db_session)
    with pytest.raises(KeyError):
        repo.take(missing_id)


@pytest.mark.parametrize(
    ("repo_factory", "missing_id", "entity"),
    [
        (
            lambda session: SqlFilmRepository(session),
            FilmID(404),
            Film(id=FilmID(404), name="x", price=Money(Decimal("1")), density=1),
        ),
        (
            lambda session: SqlSheetRepository(session),
            SheetID(404),
            Sheet(
                id=SheetID(404),
                paper=Paper(1, Decimal(1), "x", Money(Decimal("1"))),
                format=Format("f", 1, 1),
            ),
        ),
    ],
)
def test_material_catalog_replace_missing_raises_key_error(
    db_session,
    repo_factory,
    missing_id,
    entity,
):
    """``replace`` on a missing film or sheet raises ``KeyError``."""
    repo = repo_factory(db_session)
    with pytest.raises(KeyError):
        repo.replace(entity)


@pytest.mark.parametrize(
    ("repo_factory", "missing_id"),
    [
        (lambda session: SqlFilmRepository(session), FilmID(404)),
        (lambda session: SqlSheetRepository(session), SheetID(404)),
    ],
)
def test_material_catalog_delete_missing_raises_key_error(
    db_session,
    repo_factory,
    missing_id,
):
    """``delete`` on a missing film or sheet raises ``KeyError``."""
    repo = repo_factory(db_session)
    with pytest.raises(KeyError):
        repo.delete(missing_id)


def test_delete_sheet_referenced_by_part_raises_integrity_error(db_session):
    """A sheet still referenced by ``parts.sheet_id`` cannot be removed."""
    sheet_repo = SqlSheetRepository(db_session)
    sheet_id = sheet_repo.add(
        Paper(100, Decimal(1), "press", Money(Decimal("1"))),
        Format("press", 300, 200),
    )
    db_session.flush()
    db_session.add(
        PartRow(
            count=1,
            target_name="target",
            target_height=100,
            target_width=100,
            sheet_id=sheet_id.value,
            bleeds=0,
            spacing=0,
        ),
    )
    db_session.commit()

    sheet_repo.delete(sheet_id)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_delete_film_referenced_by_part_raises_integrity_error(db_session):
    """A film still referenced by ``part_laminates.film_id`` cannot be removed."""
    _, _, _, _, ctx = build_worked_run(with_laminate=True, with_cut=False, with_print=False)
    insert_catalogs_from_ctx(db_session, ctx)
    film_id = next(iter(ctx.films.keys()))
    sheet_id = next(iter(ctx.sheets.keys()))

    part = PartRow(
        count=1,
        target_name="target",
        target_height=100,
        target_width=100,
        sheet_id=sheet_id.value,
        bleeds=0,
        spacing=0,
    )
    db_session.add(part)
    db_session.flush()
    operation = PartOperationRow(part_id=part.id, position=0, kind="laminate")
    db_session.add(operation)
    db_session.flush()
    db_session.add(
        PartLaminateRow(
            operation_id=operation.id,
            laminator_id=1,
            operator_id=1,
            lamination="ONE_ZERO",
            film_id=film_id.value,
        ),
    )
    db_session.commit()

    SqlFilmRepository(db_session).delete(film_id)
    with pytest.raises(IntegrityError):
        db_session.commit()
