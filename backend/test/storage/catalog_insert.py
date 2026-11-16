"""Insert catalog domain rows through SQLAlchemy tables (not protocol save)."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TypeVar

from sqlalchemy.orm import Session

from backend.new_core.equipment.cutter import Cutter
from backend.new_core.equipment.laminator import Laminator
from backend.new_core.equipment.printer import Printer
from backend.new_core.materials.film import Film
from backend.new_core.materials.sheet import Sheet
from backend.new_core.personal.cutter_operator import CutterOperator
from backend.new_core.personal.die_cutter_operator import DieCutterOperator
from backend.new_core.personal.laminator_operator import LaminatorOperator
from backend.new_core.personal.press_operator import PressOperator
from backend.storage.equipment.printer_row import new_printer_row
from backend.storage.equipment.tables import (
    CutterRow,
    LaminatorRow,
)
from backend.storage.materials.tables import FilmRow, SheetRow
from backend.storage.personal.tables import (
    CutterOperatorRow,
    DieCutterOperatorRow,
    LaminatorOperatorRow,
    PressOperatorRow,
)
from backend.test.new_core.test_print_run import _RunPricingFixtures

_CatalogEntity = TypeVar("_CatalogEntity")


def _insert_catalog_map(
    session: Session,
    entities: Mapping[object, _CatalogEntity],
    insert: Callable[[Session, _CatalogEntity], None],
) -> None:
    for entity in entities.values():
        insert(session, entity)


def insert_printer(session: Session, printer: Printer) -> None:
    session.add(new_printer_row(printer))


def insert_laminator(session: Session, laminator: Laminator) -> None:
    session.add(
        LaminatorRow(
            id=laminator.id.value,
            name=laminator.name,
            startup=laminator.startup.amount,
        ),
    )


def insert_cutter(session: Session, cutter: Cutter) -> None:
    session.add(
        CutterRow(id=cutter.id.value, name=cutter.name, max_stack=cutter.max_stack),
    )


def insert_press_operator(session: Session, operator: PressOperator) -> None:
    session.add(
        PressOperatorRow(
            id=operator.id.value,
            name=operator.name,
            salary_by_operation=operator.salary_by_operation.amount,
        ),
    )


def insert_laminator_operator(
    session: Session,
    operator: LaminatorOperator,
) -> None:
    session.add(
        LaminatorOperatorRow(
            id=operator.id.value,
            name=operator.name,
            salary_by_operation=operator.salary_by_operation.amount,
        ),
    )


def insert_cutter_operator(session: Session, operator: CutterOperator) -> None:
    session.add(
        CutterOperatorRow(
            id=operator.id.value,
            name=operator.name,
            salary_by_operation=operator.salary_by_operation.amount,
        ),
    )


def insert_die_cutter_operator(
    session: Session,
    operator: DieCutterOperator,
) -> None:
    session.add(
        DieCutterOperatorRow(
            id=operator.id.value,
            name=operator.name,
            salary_by_operation=operator.salary_by_operation.amount,
        ),
    )


def insert_film(session: Session, film: Film) -> None:
    session.add(
        FilmRow(
            id=film.id.value,
            name=film.name,
            price=film.price.amount,
            density=film.density.value,
        ),
    )


def insert_sheet(session: Session, sheet: Sheet) -> None:
    session.add(
        SheetRow(
            id=sheet.id.value,
            paper_density=sheet.paper.density.value,
            paper_thickness=sheet.paper.thickness,
            paper_name=sheet.paper.type.value,
            paper_price_per_kilo=sheet.paper.price_per_kilo.amount,
            format_name=sheet.format.name,
            format_height=sheet.format.height,
            format_width=sheet.format.width,
        ),
    )


def insert_catalogs_from_ctx(session: Session, ctx: _RunPricingFixtures) -> None:
    """Inserts every catalog entity referenced by ``build_worked_run`` fixtures."""
    _insert_catalog_map(session, ctx.printers, insert_printer)
    _insert_catalog_map(session, ctx.press_operators, insert_press_operator)
    _insert_catalog_map(session, ctx.laminators, insert_laminator)
    _insert_catalog_map(session, ctx.laminator_operators, insert_laminator_operator)
    _insert_catalog_map(session, ctx.cutters, insert_cutter)
    _insert_catalog_map(session, ctx.cutter_operators, insert_cutter_operator)
    _insert_catalog_map(session, ctx.die_cut_operators, insert_die_cutter_operator)
    _insert_catalog_map(session, ctx.films, insert_film)
    _insert_catalog_map(session, ctx.sheets, insert_sheet)
    session.flush()
    session.commit()


def insert_minimal_order_row(session: Session, order_id: int) -> None:
    """Placeholder order row so print-run FK tests can insert runs."""
    from backend.storage.order.tables import OrderRow
    from backend.test.storage.helpers import TEST_ORDER_CREATED_AT

    session.add(
        OrderRow(
            id=order_id,
            count=1,
            description="",
            created_at=TEST_ORDER_CREATED_AT,
        ),
    )
    session.flush()
    session.commit()
