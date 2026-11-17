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
from backend.storage.order.tables import OrderRow
from backend.storage.equipment.printer_row import new_printer_row
from backend.storage.equipment.tables import (
    CutterRow,
    LaminatorRow,
)
from backend.new_core.chroma import Chroma, ChromaID
from backend.new_core.edges import Edges, EdgesID
from backend.new_core.values.percent import Percent
from backend.storage.chroma.tables import ChromaRow
from backend.storage.edges.tables import EdgesRow
from backend.storage.materials.tables import FilmRow, SheetRow
from backend.storage.personal.tables import (
    CutterOperatorRow,
    DieCutterOperatorRow,
    LaminatorOperatorRow,
    PressOperatorRow,
)
from backend.test.new_core.test_print_run import _RunPricingFixtures
from backend.test.storage.helpers import TEST_ORDER_CREATED_AT

__all__ = [
    "insert_printer",
    "insert_laminator",
    "insert_cutter",
    "insert_press_operator",
    "insert_laminator_operator",
    "insert_cutter_operator",
    "insert_die_cutter_operator",
    "insert_film",
    "insert_sheet",
    "insert_edges",
    "DEFAULT_EDGES",
    "insert_chroma",
    "DEFAULT_CHROMA",
    "insert_catalogs_from_ctx",
    "insert_minimal_order_row",
]

_CatalogEntity = TypeVar("_CatalogEntity")


def _insert_catalog_map(
    session: Session,
    entities: Mapping[object, _CatalogEntity],
    insert: Callable[[Session, _CatalogEntity], None],
) -> None:
    """Inserts each entity in the mapping with the given inserter.

    :param session: the SQLAlchemy session.
    :param entities: catalog entities keyed by id.
    :param insert: row inserter for one entity type.
    """
    for entity in entities.values():
        insert(session, entity)


def insert_printer(session: Session, printer: Printer) -> None:
    """Persists one printer row from a domain ``Printer``.

    :param session: the SQLAlchemy session.
    :param printer: the printer to insert.
    """
    session.add(new_printer_row(printer))


def insert_laminator(session: Session, laminator: Laminator) -> None:
    """Persists one laminator row from a domain ``Laminator``.

    :param session: the SQLAlchemy session.
    :param laminator: the laminator to insert.
    """
    session.add(
        LaminatorRow(
            id=laminator.id.value,
            name=laminator.name,
            startup=laminator.startup.amount,
        ),
    )


def insert_cutter(session: Session, cutter: Cutter) -> None:
    """Persists one cutter row from a domain ``Cutter``.

    :param session: the SQLAlchemy session.
    :param cutter: the cutter to insert.
    """
    session.add(
        CutterRow(
            id=cutter.id.value,
            name=cutter.name,
            max_stack=cutter.max_stack),
    )


def insert_press_operator(session: Session, operator: PressOperator) -> None:
    """Persists one press operator row.

    :param session: the SQLAlchemy session.
    :param operator: the press operator to insert.
    """
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
    """Persists one laminator operator row.

    :param session: the SQLAlchemy session.
    :param operator: the laminator operator to insert.
    """
    session.add(
        LaminatorOperatorRow(
            id=operator.id.value,
            name=operator.name,
            salary_by_operation=operator.salary_by_operation.amount,
        ),
    )


def insert_cutter_operator(session: Session, operator: CutterOperator) -> None:
    """Persists one cutter operator row.

    :param session: the SQLAlchemy session.
    :param operator: the cutter operator to insert.
    """
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
    """Persists one die-cutter operator row.

    :param session: the SQLAlchemy session.
    :param operator: the die-cutter operator to insert.
    """
    session.add(
        DieCutterOperatorRow(
            id=operator.id.value,
            name=operator.name,
            salary_by_operation=operator.salary_by_operation.amount,
        ),
    )


def insert_film(session: Session, film: Film) -> None:
    """Persists one film row from a domain ``Film``.

    :param session: the SQLAlchemy session.
    :param film: the film to insert.
    """
    session.add(
        FilmRow(
            id=film.id.value,
            name=film.name,
            price=film.price.amount,
            density=film.density.value,
        ),
    )


DEFAULT_EDGES = Edges(id=EdgesID(1), name="", bleeds=0, spacing=0)


DEFAULT_CHROMA = Chroma(
    id=ChromaID(1),
    name="4+0",
    cyan=Percent(100),
    magenta=Percent(100),
    yellow=Percent(100),
    black=Percent(100),
)


def insert_edges(session: Session, edges: Edges) -> None:
    """Persists one edges row from a domain ``Edges``.

    :param session: the SQLAlchemy session.
    :param edges: the edges row to insert.
    """
    session.add(
        EdgesRow(
            id=edges.id.value,
            name=edges.name,
            bleeds=edges.bleeds,
            spacing=edges.spacing,
        ),
    )


def insert_chroma(session: Session, chroma: Chroma) -> None:
    """Persists one chroma row from a domain ``Chroma``.

    :param session: the SQLAlchemy session.
    :param chroma: the chroma row to insert.
    """
    session.add(
        ChromaRow(
            id=chroma.id.value,
            name=chroma.name,
            cyan=chroma.cyan.value,
            magenta=chroma.magenta.value,
            yellow=chroma.yellow.value,
            black=chroma.black.value,
        ),
    )


def insert_sheet(session: Session, sheet: Sheet) -> None:
    """Persists one sheet row from a domain ``Sheet``.

    :param session: the SQLAlchemy session.
    :param sheet: the sheet to insert.
    """
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


def insert_catalogs_from_ctx(
    session: Session,
    ctx: _RunPricingFixtures,
) -> None:
    """Inserts every catalog entity from ``build_worked_run`` fixtures.

    :param session: the SQLAlchemy session.
    :param ctx: the in-memory fixture catalogs to mirror into SQL.
    """
    _insert_catalog_map(session, ctx.printers, insert_printer)
    _insert_catalog_map(session, ctx.press_operators, insert_press_operator)
    _insert_catalog_map(session, ctx.laminators, insert_laminator)
    _insert_catalog_map(
        session,
        ctx.laminator_operators,
        insert_laminator_operator)
    _insert_catalog_map(session, ctx.cutters, insert_cutter)
    _insert_catalog_map(session, ctx.cutter_operators, insert_cutter_operator)
    _insert_catalog_map(
        session,
        ctx.die_cut_operators,
        insert_die_cutter_operator)
    _insert_catalog_map(session, ctx.films, insert_film)
    _insert_catalog_map(session, ctx.sheets, insert_sheet)
    insert_edges(session, DEFAULT_EDGES)
    insert_chroma(session, DEFAULT_CHROMA)
    session.flush()
    session.commit()


def insert_minimal_order_row(session: Session, order_id: int) -> None:
    """Inserts a placeholder order row for print-run foreign-key tests.

    :param session: the SQLAlchemy session.
    :param order_id: primary key for the new order row.
    """
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
