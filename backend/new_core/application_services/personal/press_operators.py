"""Press operator catalog use cases."""

from __future__ import annotations

from backend.new_core.personal.factory import PressOperatorFactory
from backend.new_core.personal.press_operator import (
    PressOperator,
    PressOperatorID,
)
from backend.new_core.personal.press_operator_repository import (
    PressOperatorRepository,
)
from backend.new_core.values.money import Money


class PressOperatorCatalog:
    """Loads and edits press operators."""

    def __init__(
        self,
        press_operators: PressOperatorRepository,
        press_operator_factory: PressOperatorFactory,
    ) -> None:
        """Remembers the press operator store.

        :param press_operators:
        :param press_operator_factory:
        """
        self._press_operators = press_operators
        self._press_operator_factory = press_operator_factory

    def press_operators(self) -> tuple[PressOperator, ...]:
        """Returns every press operator.

        :return: rows in ascending id order.
        """
        return self._press_operators.take_all()

    def press_operator(self, operator_id: PressOperatorID) -> PressOperator:
        """Returns one press operator.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: the operator row.
        """
        return self._press_operators.take(operator_id)

    def save_press_operator(self, operator: PressOperator) -> None:
        """Stores a new press operator under its id.

        :param operator:

        :return: nothing. Existing rows are not overwritten.
        """
        self._press_operators.save(operator)

    def create_press_operator(
        self,
        name: str,
        salary_by_operation: Money,
    ) -> PressOperatorID:
        """Inserts a new press operator; the store assigns the id.

        :param name:
        :param salary_by_operation:

        :return: the assigned operator id.
        """
        operator = self._press_operator_factory.create(
            name, salary_by_operation)
        self._press_operators.save(operator)
        return operator.id

    def replace_press_operator(self, operator: PressOperator) -> None:
        """Overwrites non-id fields of an existing press operator.

        :param operator:

        :raises KeyError: if there is no operator with this id.

        :return: nothing.
        """
        self._press_operators.replace(operator)

    def delete_press_operator(self, operator_id: PressOperatorID) -> None:
        """Removes a press operator.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: nothing.
        """
        self._press_operators.delete(operator_id)
