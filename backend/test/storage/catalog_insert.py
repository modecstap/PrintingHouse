"""Insert catalog domain rows through SQLAlchemy tables (not protocol save)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.new_core.equipment.cutter import Cutter
from backend.new_core.equipment.laminator import Laminator
from backend.new_core.equipment.printer import Printer
from backend.new_core.personal.cutter_operator import CutterOperator
from backend.new_core.personal.die_cutter_operator import DieCutterOperator
from backend.new_core.personal.laminator_operator import LaminatorOperator
from backend.new_core.personal.press_operator import PressOperator
from backend.storage.equipment.tables import (
    CutterRow,
    LaminatorRow,
    PrinterRow,
)
from backend.storage.personal.tables import (
    CutterOperatorRow,
    DieCutterOperatorRow,
    LaminatorOperatorRow,
    PressOperatorRow,
)
from backend.test.new_core.test_print_run import _RunPricingFixtures


def insert_printer(session: Session, printer: Printer) -> None:
    session.add(
        PrinterRow(
            id=printer.id.value,
            startup=printer.startup.amount,
            cyan=printer.cyan.amount,
            magenta=printer.magenta.amount,
            yellow=printer.yellow.amount,
            black=printer.black.amount,
        ),
    )


def insert_laminator(session: Session, laminator: Laminator) -> None:
    session.add(
        LaminatorRow(
            id=laminator.id.value,
            startup=laminator.startup.amount,
        ),
    )


def insert_cutter(session: Session, cutter: Cutter) -> None:
    session.add(
        CutterRow(id=cutter.id.value, max_stack=cutter.max_stack),
    )


def insert_press_operator(session: Session, operator: PressOperator) -> None:
    session.add(
        PressOperatorRow(
            id=operator.id.value,
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
            salary_by_operation=operator.salary_by_operation.amount,
        ),
    )


def insert_cutter_operator(session: Session, operator: CutterOperator) -> None:
    session.add(
        CutterOperatorRow(
            id=operator.id.value,
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
            salary_by_operation=operator.salary_by_operation.amount,
        ),
    )


def insert_catalogs_from_ctx(session: Session, ctx: _RunPricingFixtures) -> None:
    """Inserts every catalog entity referenced by ``build_worked_run`` fixtures."""
    for printer in ctx.printers.values():
        insert_printer(session, printer)
    for operator in ctx.press_operators.values():
        insert_press_operator(session, operator)
    for laminator in ctx.laminators.values():
        insert_laminator(session, laminator)
    for operator in ctx.laminator_operators.values():
        insert_laminator_operator(session, operator)
    for cutter in ctx.cutters.values():
        insert_cutter(session, cutter)
    for operator in ctx.cutter_operators.values():
        insert_cutter_operator(session, operator)
    for operator in ctx.die_cut_operators.values():
        insert_die_cutter_operator(session, operator)
    session.flush()
    session.commit()


def insert_minimal_order_row(session: Session, order_id: int) -> None:
    """Placeholder order row so print-run FK tests can insert runs."""
    from backend.storage.order.tables import OrderRow

    session.add(OrderRow(id=order_id, count=1))
    session.flush()
    session.commit()
