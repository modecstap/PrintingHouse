"""Die cutter operator catalog contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)

__all__ = [
    "DieCutterOperatorIdOccupied",
    "DieCutterOperatorRepository",
]

DieCutterOperatorStoreOperation = Literal["save"]


class DieCutterOperatorIdOccupied(CatalogIdOccupied):
    """Reports that a die-cut operator id is already stored."""

    def __init__(
        self,
        operation: DieCutterOperatorStoreOperation,
        operator_id: DieCutterOperatorID,
    ) -> None:
        """Builds the repository error text.

        :param operation: the operation.
        :param operator_id: id of the operator.
        """
        super().__init__(
            f"{operation}: оператор вырубки уже есть, id={operator_id.value}",
        )


class DieCutterOperatorRepository(Protocol):
    """Loads and stores die cutter operators by id."""

    def take(self, operator_id: DieCutterOperatorID) -> DieCutterOperator:
        """Returns the die cutter operator with this id.

        :param operator_id: id of the operator.

        :raises KeyError: if there is no operator.
"""
        ...

    def take_all(self) -> tuple[DieCutterOperator, ...]:
        """Returns every stored die-cut operator.
"""
        ...

    def generate_id(self) -> DieCutterOperatorID:
        """Returns the next die cutter operator id from the store sequence.
"""
        ...

    def save(self, operator: DieCutterOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises DieCutterOperatorIdOccupied: if that id is already stored.
        """
        ...

    def replace(self, operator: DieCutterOperator) -> None:
        """Overwrites non-id fields of an existing die-cut operator.

        :param operator:

        :raises KeyError: if there is no operator with this id.
        """
        ...

    def delete(self, operator_id: DieCutterOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.
        """
        ...
