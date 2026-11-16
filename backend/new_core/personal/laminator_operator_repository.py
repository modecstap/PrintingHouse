"""Laminator operator catalog contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)

__all__ = [
    "LaminatorOperatorIdOccupied",
    "LaminatorOperatorRepository",
]

LaminatorOperatorStoreOperation = Literal["save"]


class LaminatorOperatorIdOccupied(CatalogIdOccupied):
    """Reports that a laminator operator id is already stored."""

    def __init__(
        self,
        operation: LaminatorOperatorStoreOperation,
        operator_id: LaminatorOperatorID,
    ) -> None:
        """Builds the repository error text.

        :param operation: the operation.
        :param operator_id: id of the operator.
        """
        super().__init__(
            f"{operation}: оператор ламинации уже есть, id={operator_id.value}",
        )


class LaminatorOperatorRepository(Protocol):
    """Loads and stores laminator operators by id."""

    def take(self, operator_id: LaminatorOperatorID) -> LaminatorOperator:
        """Returns the laminator operator with this id.

        :param operator_id: id of the operator.

        :raises KeyError: if there is no operator.
"""
        ...

    def take_all(self) -> tuple[LaminatorOperator, ...]:
        """Returns every stored laminator operator.
"""
        ...

    def generate_id(self) -> LaminatorOperatorID:
        """Returns the next laminator operator id from the store sequence.
"""
        ...

    def save(self, operator: LaminatorOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises LaminatorOperatorIdOccupied: if that id is already stored.
        """
        ...

    def replace(self, operator: LaminatorOperator) -> None:
        """Overwrites non-id fields of an existing laminator operator.

        :param operator:

        :raises KeyError: if there is no operator with this id.
        """
        ...

    def delete(self, operator_id: LaminatorOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.
        """
        ...
