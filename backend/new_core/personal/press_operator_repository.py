"""Press operator catalog contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.personal.press_operator import (
    PressOperator,
    PressOperatorID,
)

__all__ = [
    "PressOperatorIdOccupied",
    "PressOperatorRepository",
]

PressOperatorStoreOperation = Literal["save"]


class PressOperatorIdOccupied(CatalogIdOccupied):
    """Reports that a press operator id is already stored."""

    def __init__(
        self,
        operation: PressOperatorStoreOperation,
        operator_id: PressOperatorID,
    ) -> None:
        """Builds the repository error text.

        :param operation: the operation.
        :param operator_id: id of the operator.
        """
        super().__init__(
            f"{operation}: оператор печати уже есть, id={operator_id.value}",
        )


class PressOperatorRepository(Protocol):
    """Loads and stores press operators by id."""

    def take(self, operator_id: PressOperatorID) -> PressOperator:
        """Returns the press operator with this id.

        :param operator_id: id of the operator.

        :raises KeyError: if there is no operator.
"""
        ...

    def take_all(self) -> tuple[PressOperator, ...]:
        """Returns every stored press operator.
"""
        ...

    def generate_id(self) -> PressOperatorID:
        """Returns the next press operator id from the store sequence.
"""
        ...

    def save(self, operator: PressOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises PressOperatorIdOccupied: if that id is already stored.
        """
        ...

    def replace(self, operator: PressOperator) -> None:
        """Overwrites non-id fields of an existing press operator.

        :param operator:

        :raises KeyError: if there is no operator with this id.
        """
        ...

    def delete(self, operator_id: PressOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.
        """
        ...
