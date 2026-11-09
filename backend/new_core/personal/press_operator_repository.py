"""Press operator catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.personal.press_operator import PressOperator, PressOperatorID


class PressOperatorRepository(Protocol):
    """Loads press operators by id."""

    def take(self, operator_id: PressOperatorID) -> PressOperator:
        """Returns the press operator with this id.

        :param operator_id:

        :return: the operator row.
        """
        ...
