"""One cut of a run."""

from __future__ import annotations

from dataclasses import dataclass

from backend.new_core.equipment.cutter import Cutter
from backend.new_core.personal.cutter_operator import CutterOperator


@dataclass(frozen=True, slots=True)
class Cut:
    """
    Value Object. One cut of a run: the cutter and the operator.
    """

    cutter: Cutter
    operator_id: int
