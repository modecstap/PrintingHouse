"""Laminator operator catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)


class LaminatorOperatorRepository(Protocol):
    """Loads laminator operators by id."""

    def take(self, operator_id: LaminatorOperatorID) -> LaminatorOperator:
        """Returns the laminator operator with this id.

        :param operator_id:

        :return: the operator row.
        """
        ...
