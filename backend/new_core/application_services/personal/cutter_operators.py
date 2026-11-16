"""Cutter operator catalog use cases."""

from __future__ import annotations

from backend.new_core.personal.cutter_operator import CutterOperator, CutterOperatorID
from backend.new_core.personal.cutter_operator_repository import CutterOperatorRepository
from backend.new_core.personal.factory import CutterOperatorFactory
from backend.new_core.values.money import Money


class CutterOperatorCatalog:
    """Loads and edits cutter operators."""

    def __init__(
        self,
        cutter_operators: CutterOperatorRepository,
        cutter_operator_factory: CutterOperatorFactory,
    ) -> None:
        """Remembers the cutter operator store.

        :param cutter_operators:
        :param cutter_operator_factory:
        """
        self._cutter_operators = cutter_operators
        self._cutter_operator_factory = cutter_operator_factory

    def cutter_operators(self) -> tuple[CutterOperator, ...]:
        """Returns every cutter operator.

        :return: rows in ascending id order.
        """
        return self._cutter_operators.take_all()

    def cutter_operator(self, operator_id: CutterOperatorID) -> CutterOperator:
        """Returns one cutter operator.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: the operator row.
        """
        return self._cutter_operators.take(operator_id)

    def save_cutter_operator(self, operator: CutterOperator) -> None:
        """Stores a new cutter operator under its id.

        :param operator:

        :return: nothing. Existing rows are not overwritten.
        """
        self._cutter_operators.save(operator)

    def create_cutter_operator(
        self,
        name: str,
        salary_by_operation: Money,
    ) -> CutterOperatorID:
        """Inserts a new cutter operator; the store assigns the id.

        :param name:
        :param salary_by_operation:

        :return: the assigned operator id.
        """
        operator = self._cutter_operator_factory.create(name, salary_by_operation)
        self._cutter_operators.save(operator)
        return operator.id

    def replace_cutter_operator(self, operator: CutterOperator) -> None:
        """Overwrites non-id fields of an existing cutter operator.

        :param operator:

        :raises KeyError: if there is no operator with this id.

        :return: nothing.
        """
        self._cutter_operators.replace(operator)

    def delete_cutter_operator(self, operator_id: CutterOperatorID) -> None:
        """Removes a cutter operator.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: nothing.
        """
        self._cutter_operators.delete(operator_id)