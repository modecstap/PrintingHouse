"""Cutter operator catalog contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.personal.cutter_operator import (
    CutterOperator,
    CutterOperatorID,
)

__all__ = [
    "CutterOperatorIdOccupied",
    "CutterOperatorRepository",
]

CutterOperatorStoreOperation = Literal["save"]


class CutterOperatorIdOccupied(CatalogIdOccupied):
    """Reports that a cutter operator id is already stored."""

    def __init__(
        self,
        operation: CutterOperatorStoreOperation,
        operator_id: CutterOperatorID,
    ) -> None:
        """Builds the repository error text.

        :param operation: the operation.
        :param operator_id: id of the operator.
        """
        super().__init__(
            f"{operation}: оператор резки уже есть, id={operator_id.value}",
        )


class CutterOperatorRepository(Protocol):
    """Loads and stores cutter operators by id."""

    def take(self, operator_id: CutterOperatorID) -> CutterOperator:
        """Returns the cutter operator with this id.

        :param operator_id: id of the operator.

        :raises KeyError: if there is no operator.
"""
        ...

    def take_all(self) -> tuple[CutterOperator, ...]:
        """Returns every stored cutter operator.
"""
        ...

    def generate_id(self) -> CutterOperatorID:
        """Returns the next cutter operator id from the store sequence.
"""
        ...

    def save(self, operator: CutterOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises CutterOperatorIdOccupied: if that id is already stored.
        """
        ...

    def replace(self, operator: CutterOperator) -> None:
        """Overwrites non-id fields of an existing cutter operator.

        :param operator:

        :raises KeyError: if there is no operator with this id.
        """
        ...

    def delete(self, operator_id: CutterOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.
        """
        ...
