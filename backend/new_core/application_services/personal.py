"""Use cases that list, load, store, and remove staff catalog rows."""

from __future__ import annotations

from backend.new_core.personal.cutter_operator import CutterOperator, CutterOperatorID
from backend.new_core.personal.cutter_operator_repository import CutterOperatorRepository
from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.new_core.personal.die_cutter_operator_repository import (
    DieCutterOperatorRepository,
)
from backend.new_core.personal.factory import (
    CutterOperatorFactory,
    DieCutterOperatorFactory,
    LaminatorOperatorFactory,
    PressOperatorFactory,
)
from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)
from backend.new_core.personal.laminator_operator_repository import (
    LaminatorOperatorRepository,
)
from backend.new_core.personal.press_operator import PressOperator, PressOperatorID
from backend.new_core.personal.press_operator_repository import PressOperatorRepository
from backend.new_core.values.money import Money


class StaffCatalogService:
    """Loads and edits press, laminate, cut, and die-cut operators."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        press_operators: PressOperatorRepository,
        laminator_operators: LaminatorOperatorRepository,
        cutter_operators: CutterOperatorRepository,
        die_cut_operators: DieCutterOperatorRepository,
        press_operator_factory: PressOperatorFactory,
        laminator_operator_factory: LaminatorOperatorFactory,
        cutter_operator_factory: CutterOperatorFactory,
        die_cut_operator_factory: DieCutterOperatorFactory,
    ) -> None:
        """Remembers the operator stores.

        :param press_operators:
        :param laminator_operators:
        :param cutter_operators:
        :param die_cut_operators:
        :param press_operator_factory:
        :param laminator_operator_factory:
        :param cutter_operator_factory:
        :param die_cut_operator_factory:
        """
        self._press_operators = press_operators
        self._laminator_operators = laminator_operators
        self._cutter_operators = cutter_operators
        self._die_cut_operators = die_cut_operators
        self._press_operator_factory = press_operator_factory
        self._laminator_operator_factory = laminator_operator_factory
        self._cutter_operator_factory = cutter_operator_factory
        self._die_cut_operator_factory = die_cut_operator_factory

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
        operator = self._press_operator_factory.create(name, salary_by_operation)
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
        operator = self._laminator_operator_factory.create(name, salary_by_operation)
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

    def die_cut_operators(self) -> tuple[DieCutterOperator, ...]:
        """Returns every die-cut operator.

        :return: rows in ascending id order.
        """
        return self._die_cut_operators.take_all()

    def die_cut_operator(
        self,
        operator_id: DieCutterOperatorID,
    ) -> DieCutterOperator:
        """Returns one die-cut operator.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: the operator row.
        """
        return self._die_cut_operators.take(operator_id)

    def save_die_cut_operator(self, operator: DieCutterOperator) -> None:
        """Stores a new die-cut operator under its id.

        :param operator:

        :return: nothing. Existing rows are not overwritten.
        """
        self._die_cut_operators.save(operator)

    def create_die_cut_operator(
        self,
        name: str,
        salary_by_operation: Money,
    ) -> DieCutterOperatorID:
        """Inserts a new die-cut operator; the store assigns the id.

        :param name:
        :param salary_by_operation:

        :return: the assigned operator id.
        """
        operator = self._die_cut_operator_factory.create(name, salary_by_operation)
        self._die_cut_operators.save(operator)
        return operator.id

    def replace_die_cut_operator(self, operator: DieCutterOperator) -> None:
        """Overwrites non-id fields of an existing die-cut operator.

        :param operator:

        :raises KeyError: if there is no operator with this id.

        :return: nothing.
        """
        self._die_cut_operators.replace(operator)

    def delete_die_cut_operator(
        self,
        operator_id: DieCutterOperatorID,
    ) -> None:
        """Removes a die-cut operator.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: nothing.
        """
        self._die_cut_operators.delete(operator_id)
