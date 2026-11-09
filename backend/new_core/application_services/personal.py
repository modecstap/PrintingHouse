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
from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)
from backend.new_core.personal.laminator_operator_repository import (
    LaminatorOperatorRepository,
)
from backend.new_core.personal.press_operator import PressOperator, PressOperatorID
from backend.new_core.personal.press_operator_repository import PressOperatorRepository


class StaffCatalogService:
    """Loads and edits press, laminate, cut, and die-cut operators."""

    def __init__(
        self,
        press_operators: PressOperatorRepository,
        laminator_operators: LaminatorOperatorRepository,
        cutter_operators: CutterOperatorRepository,
        die_cut_operators: DieCutterOperatorRepository,
    ) -> None:
        """Remembers the operator stores.

        :param press_operators:
        :param laminator_operators:
        :param cutter_operators:
        :param die_cut_operators:
        """
        self._press_operators = press_operators
        self._laminator_operators = laminator_operators
        self._cutter_operators = cutter_operators
        self._die_cut_operators = die_cut_operators

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
