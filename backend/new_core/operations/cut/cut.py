"""One cut of a run."""

from __future__ import annotations

from dataclasses import dataclass

from backend.new_core.equipment.cutter import CutterID
from backend.new_core.personal.cutter_operator import CutterOperatorID


@dataclass(frozen=True, slots=True)
class Cut:
    """
    Value Object. One cut of a run: the cutter id and the operator.
    """

    cutter_id: CutterID
    operator_id: CutterOperatorID
