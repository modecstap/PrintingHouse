"""Maps part rows and operation subtypes to domain parts."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.new_core.format import Format
from backend.new_core.materials.film import FilmID
from backend.new_core.materials.sheet import SheetID
from backend.new_core.operations.cut.cut import Cut
from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.operations.laminate.laminate import Laminate
from backend.new_core.operations.laminate.lamination import Lamination
from backend.new_core.operations.print.chroma import Chroma
from backend.new_core.operations.print.print import Print
from backend.new_core.operations.run_operation import RunOperation
from backend.new_core.part import Part
from backend.new_core.print_run.imposition import Imposition
from backend.new_core.values.percent import Percent
from backend.new_core.equipment.cutter import CutterID
from backend.new_core.equipment.laminator import LaminatorID
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.personal.cutter_operator import CutterOperatorID
from backend.new_core.personal.die_cutter_operator import DieCutterOperatorID
from backend.new_core.personal.laminator_operator import LaminatorOperatorID
from backend.new_core.personal.press_operator import PressOperatorID
from backend.storage.materials.sheet_repository import SqlSheetRepository
from backend.storage.part.tables import (
    PartCutRow,
    PartDieCutRow,
    PartLaminateRow,
    PartOperationRow,
    PartPrintRow,
    PartRow,
)


def part_row_to_part(session: Session, part_id: int) -> Part:
    """Loads a ``Part`` graph for the stored part id.

    :param session:
    :param part_id:

    :return: the domain part with operations in position order.
    """
    row = session.get(PartRow, part_id)
    if row is None:
        raise LookupError(f"part id={part_id}")

    sheet_id = SheetID(row.sheet_id)
    sheet = SqlSheetRepository(session).take(sheet_id)
    imposition = Imposition(
        target=Format(row.target_name, row.target_height, row.target_width),
        sheet_id=sheet_id,
        press_sheet=sheet,
        bleeds=row.bleeds,
        spacing=row.spacing,
    )
    operations = _load_operations(session, part_id)
    return Part(
        imposition=imposition,
        count=row.count,
        operations=operations,
    )


def persist_part(session: Session, part: Part, *, markup: int = 0) -> int:
    """Writes a ``Part`` and its operations; returns the new part row id.

    :param session:
    :param part:

    :return: the generated ``parts.id``.
    """
    imp = part.imposition
    if imp.press_sheet is None:
        raise RuntimeError("cannot persist part with unhydrated imposition")
    row = PartRow(
        count=part.count,
        markup=markup,
        target_name=imp.target.name,
        target_height=imp.target.height,
        target_width=imp.target.width,
        sheet_id=imp.sheet_id.value,
        bleeds=imp.bleeds,
        spacing=imp.spacing,
    )
    session.add(row)
    session.flush()
    for position, operation in enumerate(part.operations):
        kind = _operation_kind(operation)
        op_row = PartOperationRow(
            part_id=row.id,
            position=position,
            kind=kind,
        )
        session.add(op_row)
        session.flush()
        _persist_operation_subtype(session, op_row.id, operation, kind)
    return row.id


def _load_operations(session: Session, part_id: int) -> tuple[RunOperation, ...]:
    stmt = (
        select(PartOperationRow)
        .where(PartOperationRow.part_id == part_id)
        .order_by(PartOperationRow.position)
    )
    op_rows = session.execute(stmt).scalars().all()
    loaded: list[RunOperation] = []
    for op_row in op_rows:
        loaded.append(_load_operation_subtype(session, op_row))
    return tuple(loaded)


def _load_operation_subtype(
    session: Session,
    op_row: PartOperationRow,
) -> RunOperation:
    if op_row.kind == "print":
        sub = session.get(PartPrintRow, op_row.id)
        if sub is None:
            raise RuntimeError(f"missing part_prints for operation id={op_row.id}")
        return Print(
            printer_id=PrinterID(sub.printer_id),
            operator_id=PressOperatorID(sub.operator_id),
            chroma=Chroma[sub.chroma],
        )
    if op_row.kind == "laminate":
        sub = session.get(PartLaminateRow, op_row.id)
        if sub is None:
            raise RuntimeError(f"missing part_laminates for operation id={op_row.id}")
        return Laminate(
            laminator_id=LaminatorID(sub.laminator_id),
            operator_id=LaminatorOperatorID(sub.operator_id),
            lamination=Lamination[sub.lamination],
            film_id=FilmID(sub.film_id),
        )
    if op_row.kind == "cut":
        sub = session.get(PartCutRow, op_row.id)
        if sub is None:
            raise RuntimeError(f"missing part_cuts for operation id={op_row.id}")
        return Cut(
            cutter_id=CutterID(sub.cutter_id),
            operator_id=CutterOperatorID(sub.operator_id),
        )
    if op_row.kind == "die_cut":
        sub = session.get(PartDieCutRow, op_row.id)
        if sub is None:
            raise RuntimeError(f"missing part_die_cuts for operation id={op_row.id}")
        return DieCut(operator_id=DieCutterOperatorID(sub.operator_id))
    raise RuntimeError(f"unknown operation kind {op_row.kind!r}")


def _persist_operation_subtype(
    session: Session,
    operation_id: int,
    operation: RunOperation,
    kind: str,
) -> None:
    if kind == "print":
        assert isinstance(operation, Print)
        session.add(
            PartPrintRow(
                operation_id=operation_id,
                printer_id=operation.printer_id.value,
                operator_id=operation.operator_id.value,
                chroma=operation.chroma.name,
            ),
        )
        return
    if kind == "laminate":
        assert isinstance(operation, Laminate)
        session.add(
            PartLaminateRow(
                operation_id=operation_id,
                laminator_id=operation.laminator_id.value,
                operator_id=operation.operator_id.value,
                lamination=operation.lamination.name,
                film_id=operation.film_id.value,
            ),
        )
        return
    if kind == "cut":
        assert isinstance(operation, Cut)
        session.add(
            PartCutRow(
                operation_id=operation_id,
                cutter_id=operation.cutter_id.value,
                operator_id=operation.operator_id.value,
            ),
        )
        return
    if kind == "die_cut":
        assert isinstance(operation, DieCut)
        session.add(
            PartDieCutRow(
                operation_id=operation_id,
                operator_id=operation.operator_id.value,
            ),
        )
        return
    raise RuntimeError(f"unknown operation kind {kind!r}")


def _operation_kind(operation: RunOperation) -> str:
    if isinstance(operation, Print):
        return "print"
    if isinstance(operation, Laminate):
        return "laminate"
    if isinstance(operation, Cut):
        return "cut"
    if isinstance(operation, DieCut):
        return "die_cut"
    raise RuntimeError(f"unsupported operation type {type(operation)!r}")
