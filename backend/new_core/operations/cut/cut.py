"""One cut of a run."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

from typing import TYPE_CHECKING

from backend.new_core.values.money import Money

if TYPE_CHECKING:
    from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.equipment.cutter import Cutter
from backend.new_core.personal.cutter_operator import CutterOperator


@dataclass(frozen=True, slots=True)
class Cut:
    """
    Value Object. One cut of a run: the cutter and the operator.
    """

    cutter: Cutter
    operator: CutterOperator

    def material_price(self, run: PrintRun) -> Money:
        """Returns no material for a cut.

        :return: zero.
        """
        return Money.zero()

    def work_price(self, run: PrintRun) -> Money:
        """Returns the cutter salary for one press sheet.

        :return: the salary times the human cuts, divided by the press sheet
        count. Human cuts are the stack lifts times the cut count. A lift
        count is the press sheet count divided by the sheets in a stack,
        rounded up.
        """
        stack = self._sheets_in_stack(run)
        lifts = (
                Decimal(run.imposition_count()) / Decimal(stack)
        ).to_integral_value(rounding=ROUND_CEILING)
        human_cuts = int(lifts) * run.imposition.cuts()
        return (
                self.operator.salary_by_operation
                * human_cuts
                / run.imposition_count()
        )

    def startup_price(self, run: PrintRun) -> Money:
        """Returns no startup for a cut.

        :return: zero.
        """
        return Money.zero()

    def _sheets_in_stack(self, run: PrintRun) -> int:
        """Returns how many press sheets fit in one cutter stack.

        :return: the stack height divided by the press sheet thickness,
        rounded up to an integer, then raised to zero when that integer
        is negative.
        """
        sheets = (
                Decimal(self.cutter.max_stack)
                / run.imposition.thickness()
        ).to_integral_value(rounding=ROUND_CEILING)
        return max(int(sheets), 0)
