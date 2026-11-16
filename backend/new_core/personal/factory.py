"""Builds staff catalog rows with ids from the store."""

from __future__ import annotations

from backend.new_core.personal.cutter_operator import CutterOperator
from backend.new_core.personal.cutter_operator_repository import (
    CutterOperatorRepository,
)
from backend.new_core.personal.die_cutter_operator import DieCutterOperator
from backend.new_core.personal.die_cutter_operator_repository import (
    DieCutterOperatorRepository,
)
from backend.new_core.personal.laminator_operator import LaminatorOperator
from backend.new_core.personal.laminator_operator_repository import (
    LaminatorOperatorRepository,
)
from backend.new_core.personal.press_operator import PressOperator
from backend.new_core.personal.press_operator_repository import (
    PressOperatorRepository,
)
from backend.new_core.values.money import Money


__all__ = [
    "PressOperatorFactory",
    "LaminatorOperatorFactory",
    "CutterOperatorFactory",
    "DieCutterOperatorFactory",
]

class PressOperatorFactory:
    """Allocates press-operator ids and builds rows."""

    def __init__(self, press_operators: PressOperatorRepository) -> None:
        """Initializes this instance.

        :param press_operators: the press operators.
        """
        self._press_operators = press_operators

    def create(self, name: str, salary_by_operation: Money) -> PressOperator:
        """Builds a press operator with a generated id.

        :param name: the name.
        :param salary_by_operation: the salary by operation.

        :return: the PressOperator result.
        """
        return PressOperator(
            id=self._press_operators.generate_id(),
            name=name,
            salary_by_operation=salary_by_operation,
        )


class LaminatorOperatorFactory:
    """Allocates laminator-operator ids and builds rows."""

    def __init__(
            self,
            laminator_operators: LaminatorOperatorRepository) -> None:
        """Initializes this instance.

        :param laminator_operators: the laminator operators.
        """
        self._laminator_operators = laminator_operators

    def create(
            self,
            name: str,
            salary_by_operation: Money) -> LaminatorOperator:
        """Builds a laminator operator with a generated id.

        :param name: the name.
        :param salary_by_operation: the salary by operation.

        :return: the LaminatorOperator result.
        """
        return LaminatorOperator(
            id=self._laminator_operators.generate_id(),
            name=name,
            salary_by_operation=salary_by_operation,
        )


class CutterOperatorFactory:
    """Allocates cutter-operator ids and builds rows."""

    def __init__(self, cutter_operators: CutterOperatorRepository) -> None:
        """Initializes this instance.

        :param cutter_operators: the cutter operators.
        """
        self._cutter_operators = cutter_operators

    def create(self, name: str, salary_by_operation: Money) -> CutterOperator:
        """Builds a cutter operator with a generated id.

        :param name: the name.
        :param salary_by_operation: the salary by operation.

        :return: the CutterOperator result.
        """
        return CutterOperator(
            id=self._cutter_operators.generate_id(),
            name=name,
            salary_by_operation=salary_by_operation,
        )


class DieCutterOperatorFactory:
    """Allocates die-cut-operator ids and builds rows."""

    def __init__(self, die_cut_operators: DieCutterOperatorRepository) -> None:
        """Initializes this instance.

        :param die_cut_operators: the die cut operators.
        """
        self._die_cut_operators = die_cut_operators

    def create(
            self,
            name: str,
            salary_by_operation: Money) -> DieCutterOperator:
        """Builds a die-cut operator with a generated id.

        :param name: the name.
        :param salary_by_operation: the salary by operation.

        :return: the DieCutterOperator result.
        """
        return DieCutterOperator(
            id=self._die_cut_operators.generate_id(),
            name=name,
            salary_by_operation=salary_by_operation,
        )
