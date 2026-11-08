"""One die cut of a press sheet."""

from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

from backend.new_core.values.money import Money

if TYPE_CHECKING:
    from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.personal.die_cutter_operator import DieCutterOperator


@dataclass(frozen=True, slots=True)
class DieCut:
    """
    Value Object. One die cut of a press sheet, priced from the operator salary.
    """

    operator: DieCutterOperator

    def material_price(self, run: PrintRun) -> Money:
        """Returns no material for a die cut.

        :return: zero.
        """
        return Money.zero()

    def work_price(self, run: PrintRun) -> Money:
        """Returns the die cutter salary for one press sheet.

        :return: the full salary.
        """
        return self.operator.salary_by_operation

    def startup_price(self, run: PrintRun) -> Money:
        """Returns no startup for a die cut.

        :return: zero.
        """
        return Money.zero()
