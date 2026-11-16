"""Die-cut operator catalog use cases."""

from __future__ import annotations

from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.new_core.personal.die_cutter_operator_repository import (
    DieCutterOperatorRepository,
)
from backend.new_core.personal.factory import DieCutterOperatorFactory
from backend.new_core.values.money import Money


__all__ = ["DieCutterOperatorCatalog"]

class DieCutterOperatorCatalog:
    """Loads and edits die-cut operators."""

    def __init__(
        self,
        die_cut_operators: DieCutterOperatorRepository,
        die_cut_operator_factory: DieCutterOperatorFactory,
    ) -> None:
        """Remembers the die-cut operator store.

        :param die_cut_operators: the die cut operators.
        :param die_cut_operator_factory: the die cut operator factory.
        """
        self._die_cut_operators = die_cut_operators
        self._die_cut_operator_factory = die_cut_operator_factory

    def die_cut_operators(self) -> tuple[DieCutterOperator, ...]:
        """Returns every die-cut operator.

        :return: the tuple[DieCutterOperator, ...] result.
        """
        return self._die_cut_operators.take_all()

    def die_cut_operator(
        self,
        operator_id: DieCutterOperatorID,
    ) -> DieCutterOperator:
        """Returns one die-cut operator.

        :param operator_id: id of the operator.

        :raises KeyError: if there is no operator.

        :return: the DieCutterOperator result.
        """
        return self._die_cut_operators.take(operator_id)

    def save_die_cut_operator(self, operator: DieCutterOperator) -> None:
        """Stores a new die-cut operator under its id.

        :param operator: the operator.
        """
        self._die_cut_operators.save(operator)

    def create_die_cut_operator(
        self,
        name: str,
        salary_by_operation: Money,
    ) -> DieCutterOperatorID:
        """Inserts a new die-cut operator; the store assigns the id.

        :param name: the name.
        :param salary_by_operation: the salary by operation.

        :return: the DieCutterOperatorID result.
        """
        operator = self._die_cut_operator_factory.create(
            name, salary_by_operation)
        self._die_cut_operators.save(operator)
        return operator.id

    def replace_die_cut_operator(self, operator: DieCutterOperator) -> None:
        """Overwrites non-id fields of an existing die-cut operator.

        :param operator:

        :raises KeyError: if there is no operator with this id.
        """
        self._die_cut_operators.replace(operator)

    def delete_die_cut_operator(
        self,
        operator_id: DieCutterOperatorID,
    ) -> None:
        """Removes a die-cut operator.

        :param operator_id:

        :raises KeyError: if there is no operator.
        """
        self._die_cut_operators.delete(operator_id)
