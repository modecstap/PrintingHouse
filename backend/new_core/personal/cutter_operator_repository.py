"""Cutter operator catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.personal.cutter_operator import CutterOperator, CutterOperatorID


class CutterOperatorRepository(Protocol):
    """Loads cutter operators by id."""

    def take(self, operator_id: CutterOperatorID) -> CutterOperator:
        """Returns the cutter operator with this id.

        :param operator_id:

        :return: the operator row.
        """
        ...
