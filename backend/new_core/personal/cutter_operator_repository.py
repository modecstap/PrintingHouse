"""Cutter operator catalog contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.personal.cutter_operator import CutterOperator, CutterOperatorID

CutterOperatorStoreOperation = Literal["save"]


class CutterOperatorIdOccupied(CatalogIdOccupied):
    """Reports that a cutter operator id is already stored."""

    def __init__(
        self,
        operation: CutterOperatorStoreOperation,
        operator_id: CutterOperatorID,
    ) -> None:
        """Builds the repository error text.

        :param operation:
        :param operator_id:

        :return: sets the message
        ``{operation}: оператор резки уже есть, id={operator_id.value}``.
        """
        super().__init__(
            f"{operation}: оператор резки уже есть, id={operator_id.value}",
        )


class CutterOperatorRepository(Protocol):
    """Loads and stores cutter operators by id."""

    def take(self, operator_id: CutterOperatorID) -> CutterOperator:
        """Returns the cutter operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: the operator row.
        """
        ...

    def take_all(self) -> tuple[CutterOperator, ...]:
        """Returns every stored cutter operator.

        :return: operators in ascending id order.
        """
        ...

    def save(self, operator: CutterOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises CutterOperatorIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        ...

    def delete(self, operator_id: CutterOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: nothing.
        """
        ...
