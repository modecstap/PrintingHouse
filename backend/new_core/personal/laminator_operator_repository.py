"""Laminator operator catalog contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)

LaminatorOperatorStoreOperation = Literal["save"]


class LaminatorOperatorIdOccupied(CatalogIdOccupied):
    """Reports that a laminator operator id is already stored."""

    def __init__(
        self,
        operation: LaminatorOperatorStoreOperation,
        operator_id: LaminatorOperatorID,
    ) -> None:
        """Builds the repository error text.

        :param operation:
        :param operator_id:

        :return: sets the message
        ``{operation}: оператор ламинации уже есть, id={operator_id.value}``.
        """
        super().__init__(
            f"{operation}: оператор ламинации уже есть, id={operator_id.value}",
        )


class LaminatorOperatorRepository(Protocol):
    """Loads and stores laminator operators by id."""

    def take(self, operator_id: LaminatorOperatorID) -> LaminatorOperator:
        """Returns the laminator operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: the operator row.
        """
        ...

    def take_all(self) -> tuple[LaminatorOperator, ...]:
        """Returns every stored laminator operator.

        :return: operators in ascending id order.
        """
        ...

    def save(self, operator: LaminatorOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises LaminatorOperatorIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        ...

    def delete(self, operator_id: LaminatorOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: nothing.
        """
        ...
