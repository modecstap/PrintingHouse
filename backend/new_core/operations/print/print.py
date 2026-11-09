"""One print of a press target."""

from __future__ import annotations

from dataclasses import dataclass

from backend.new_core.materials.sheet import Sheet

from backend.new_core.operations.print.chroma import Chroma

@dataclass(frozen=True, slots=True)
class Print:
    """
    Value Object. One print of a press target: the specification, the printer, and the operator.
    """

    printer_id: int
    operator_id: int
    chroma: Chroma
    paper: Sheet

