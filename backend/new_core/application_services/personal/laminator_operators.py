"""Laminator operator catalog use cases."""

from __future__ import annotations

from backend.new_core.personal.factory import LaminatorOperatorFactory
from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)
from backend.new_core.personal.laminator_operator_repository import (
    LaminatorOperatorRepository,
)
from backend.new_core.values.money import Money


class LaminatorOperatorCatalog:
    """Loads and edits laminator operators."""

    def __init__(
        self,
        laminator_operators: LaminatorOperatorRepository,
        laminator_operator_factory: LaminatorOperatorFactory,
    ) -> None:
        """Remembers the laminator operator store.

        :param laminator_operators:
        :param laminator_operator_factory:
        """
        self._laminator_operators = laminator_operators
        self._laminator_operator_factory = laminator_operator_factory

    def laminator_operators(self) -> tuple[LaminatorOperator, ...]:
        """Returns every laminator operator.

        :return: rows in ascending id order.
        """
        return self._laminator_operators.take_all()

    def laminator_operator(
        self,
        operator_id: LaminatorOperatorID,
    ) -> LaminatorOperator:
        """Returns one laminator operator.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: the operator row.
        """
        return self._laminator_operators.take(operator_id)

    def save_laminator_operator(self, operator: LaminatorOperator) -> None:
        """Stores a new laminator operator under its id.

        :param operator:

        :return: nothing. Existing rows are not overwritten.
        """
        self._laminator_operators.save(operator)

    def create_laminator_operator(
        self,
        name: str,
        salary_by_operation: Money,
    ) -> LaminatorOperatorID:
        """Inserts a new laminator operator; the store assigns the id.

        :param name:
        :param salary_by_operation:

        :return: the assigned operator id.
        """
        operator = self._laminator_operator_factory.create(
            name, salary_by_operation)
        self._laminator_operators.save(operator)
        return operator.id

    def replace_laminator_operator(self, operator: LaminatorOperator) -> None:
        """Overwrites non-id fields of an existing laminator operator.

        :param operator:

        :raises KeyError: if there is no operator with this id.

        :return: nothing.
        """
        self._laminator_operators.replace(operator)

    def delete_laminator_operator(
        self,
        operator_id: LaminatorOperatorID,
    ) -> None:
        """Removes a laminator operator.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: nothing.
        """
        self._laminator_operators.delete(operator_id)
