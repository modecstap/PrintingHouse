"""Die cutter operator catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)


class DieCutterOperatorRepository(Protocol):
    """Loads die cutter operators by id."""

    def take(self, operator_id: DieCutterOperatorID) -> DieCutterOperator:
        """Returns the die cutter operator with this id.

        :param operator_id:

        :return: the operator row.
        """
        ...
