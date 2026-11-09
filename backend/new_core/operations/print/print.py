"""One print of a press target."""

from __future__ import annotations

from dataclasses import dataclass

from backend.new_core.materials.sheet import Sheet
from backend.new_core.operations.print.chroma import Chroma
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.personal.press_operator import PressOperatorID

@dataclass(frozen=True, slots=True)
class Print:
    """
    Value Object. One print of a press target: the specification, the printer, and the operator.
    """

    printer_id: PrinterID
    operator_id: PressOperatorID
    chroma: Chroma
    paper: Sheet

