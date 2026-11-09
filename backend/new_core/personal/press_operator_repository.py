"""Press operator catalog contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.personal.press_operator import PressOperator, PressOperatorID

PressOperatorStoreOperation = Literal["save"]


class PressOperatorIdOccupied(CatalogIdOccupied):
    """Reports that a press operator id is already stored."""

    def __init__(
        self,
        operation: PressOperatorStoreOperation,
        operator_id: PressOperatorID,
    ) -> None:
        """Builds the repository error text.

        :param operation:
        :param operator_id:

        :return: sets the message
        ``{operation}: оператор печати уже есть, id={operator_id.value}``.
        """
        super().__init__(
            f"{operation}: оператор печати уже есть, id={operator_id.value}",
        )


class PressOperatorRepository(Protocol):
    """Loads and stores press operators by id."""

    def take(self, operator_id: PressOperatorID) -> PressOperator:
        """Returns the press operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: the operator row.
        """
        ...

    def take_all(self) -> tuple[PressOperator, ...]:
        """Returns every stored press operator.

        :return: operators in ascending id order.
        """
        ...

    def save(self, operator: PressOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises PressOperatorIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        ...

    def delete(self, operator_id: PressOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: nothing.
        """
        ...
