"""Maps part rows and operation subtypes to domain parts."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.new_core.format import Format
from backend.new_core.materials.film import FilmID
from backend.new_core.materials.sheet import SheetID
from backend.new_core.operations.cut.cut import Cut
from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.operations.laminate.laminate import Laminate
from backend.new_core.operations.laminate.lamination import Lamination
from backend.new_core.chroma import Chroma
from backend.new_core.operations.print.print import Print
from backend.new_core.operations.run_operation import RunOperation
from backend.new_core.part import Part
from backend.new_core.print_run.imposition import Imposition
from backend.new_core.equipment.cutter import CutterID
from backend.new_core.equipment.laminator import LaminatorID
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.personal.cutter_operator import CutterOperatorID
from backend.new_core.personal.die_cutter_operator import DieCutterOperatorID
from backend.new_core.personal.laminator_operator import LaminatorOperatorID
from backend.new_core.personal.press_operator import PressOperatorID
from backend.new_core.edges import EdgesID
from backend.storage.edges.edges_repository import SqlEdgesRepository
from backend.storage.materials.sheet_repository import SqlSheetRepository
from backend.storage.part.tables import (
    PartCutRow,
    PartDieCutRow,
    PartLaminateRow,
    PartOperationRow,
    PartPrintRow,
    PartRow,
)


__all__ = [
    "part_row_to_part",
    "persist_part",
]

def part_row_to_part(session: Session, part_id: int) -> Part:
    """Loads a ``Part`` graph for the stored part id.

    :param session: database session.
    :param part_id: id of the part.

    :raises LookupError: when the operation fails.

    :return: the Part result.
    """
    row = session.get(PartRow, part_id)
    if row is None:
        raise LookupError(f"part id={part_id}")

    sheet_id = SheetID(row.sheet_id)
    sheet = SqlSheetRepository(session).take(sheet_id)
    edges = SqlEdgesRepository(session).take(EdgesID(row.edges_id))
    imposition = Imposition(
        target=Format(row.target_name, row.target_height, row.target_width),
        press_sheet=sheet,
        edges=edges,
    )
    operations = _load_operations(session, part_id)
    return Part(
        imposition=imposition,
        count=row.count,
        need_spacing=False,
        operations=operations,
    )


def persist_part(session: Session, part: Part) -> int:
    """Writes a ``Part`` and its operations; returns the new part row id.

    :param session: database session.
    :param part: the part.

    :return: the int result.
    """
    imp = part.imposition
    edges_repo = SqlEdgesRepository(session)
    if imp.edges.id.value > 0:
        edges_id = imp.edges.id.value
    else:
        edges_id = edges_repo.find_or_add(
            imp.edges.name,
            imp.edges.bleeds,
            imp.edges.spacing,
        ).value
    row = PartRow(
        count=part.count,
        target_name=imp.target.name,
        target_height=imp.target.height,
        target_width=imp.target.width,
        sheet_id=imp.press_sheet.id.value,
        edges_id=edges_id,
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
        _persist_operation_subtype(session, op_row.id, operation)
    return row.id


def _load_operations(
        session: Session, part_id: int) -> tuple[RunOperation, ...]:
    """Handles load operations.

    :param session: database session.
    :param part_id: id of the part.

    :return: the tuple[RunOperation, ...] result.
    """
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


def _require_subtype_row(
    row: object | None,
    table: str,
    operation_id: int,
) -> object:
    """Handles require subtype row.

    :param row: the row.
    :param table: the table.
    :param operation_id: id of the operation.

    :raises RuntimeError: when the operation fails.

    :return: the object result.
    """
    if row is None:
        raise RuntimeError(f"missing {table} for operation id={operation_id}")
    return row


def _load_operation_subtype(
    session: Session,
    op_row: PartOperationRow,
) -> RunOperation:
    """Handles load operation subtype.

    :param session: database session.
    :param op_row: the op row.

    :raises RuntimeError: when the operation fails.

    :return: the RunOperation result.
    """
    if op_row.kind == "print":
        sub = _require_subtype_row(
            session.get(PartPrintRow, op_row.id),
            "part_prints",
            op_row.id,
        )
        return Print(
            printer_id=PrinterID(sub.printer_id),
            operator_id=PressOperatorID(sub.operator_id),
            chroma=Chroma[sub.chroma],
        )
    if op_row.kind == "laminate":
        sub = _require_subtype_row(
            session.get(PartLaminateRow, op_row.id),
            "part_laminates",
            op_row.id,
        )
        return Laminate(
            laminator_id=LaminatorID(sub.laminator_id),
            operator_id=LaminatorOperatorID(sub.operator_id),
            lamination=Lamination[sub.lamination],
            film_id=FilmID(sub.film_id),
        )
    if op_row.kind == "cut":
        sub = _require_subtype_row(
            session.get(PartCutRow, op_row.id),
            "part_cuts",
            op_row.id,
        )
        return Cut(
            cutter_id=CutterID(sub.cutter_id),
            operator_id=CutterOperatorID(sub.operator_id),
        )
    if op_row.kind == "die_cut":
        sub = _require_subtype_row(
            session.get(PartDieCutRow, op_row.id),
            "part_die_cuts",
            op_row.id,
        )
        return DieCut(operator_id=DieCutterOperatorID(sub.operator_id))
    raise RuntimeError(f"unknown operation kind {op_row.kind!r}")


def _persist_operation_subtype(
    session: Session,
    operation_id: int,
    operation: RunOperation,
) -> None:
    """Handles persist operation subtype.

    :param session: database session.
    :param operation_id: id of the operation.
    :param operation: the operation.

    :raises RuntimeError: when the operation fails.
    """
    kind = _operation_kind(operation)
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
    """Handles operation kind.

    :param operation: the operation.

    :raises RuntimeError: when the operation fails.

    :return: the str result.
    """
    if isinstance(operation, Print):
        return "print"
    if isinstance(operation, Laminate):
        return "laminate"
    if isinstance(operation, Cut):
        return "cut"
    if isinstance(operation, DieCut):
        return "die_cut"
    raise RuntimeError(f"unsupported operation type {type(operation)!r}")
