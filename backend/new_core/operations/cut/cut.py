"""One cut of a run."""

from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

from backend.new_core.values.money import Money
from backend.new_core.print_run.imposition import Imposition
from backend.new_core.operations.cut.cutter import Cutter
from backend.new_core.operations.cut.cutter_operator import CutterOperator


@dataclass(frozen=True, slots=True)
class Cut:
    """
    Value Object. One cut of a run: the cutter, the operator, the imposition,
    and the press-sheet count.
    """

    cutter: Cutter
    operator: CutterOperator
    imposition: Imposition
    sheet_count: int

    @staticmethod
    def material_price() -> Money:
        """Returns no material for a cut.

        :return: zero.
        """
        return Money.zero()

    def work_price(self) -> Money:
        """Returns the cutter salary for one press sheet.

        :return: the salary times the human cuts, divided by the press sheet
        count. Human cuts are the stack lifts times the cut count. A lift
        count is the press sheet count divided by the sheets in a stack,
        rounded up.
        """
        stack = self._sheets_in_stack()
        lifts = (
            Decimal(self.sheet_count) / Decimal(stack)
        ).to_integral_value(rounding=ROUND_CEILING)
        human_cuts = int(lifts) * self.imposition.cuts()
        return (
                self.operator.salary_by_operation
                * human_cuts
                / self.sheet_count
        )

    @staticmethod
    def startup_price() -> Money:
        """Returns no startup for a cut.

        :return: zero.
        """
        return Money.zero()

    def _sheets_in_stack(self) -> int:
        """Returns how many press sheets fit in one cutter stack.

        :return: the stack height divided by the press sheet thickness,
        rounded up to an integer, then raised to zero when that integer
        is negative.
        """
        sheets = (
                Decimal(self.cutter.max_stack)
                / self.imposition.press_sheet.thickness()
        ).to_integral_value(rounding=ROUND_CEILING)
        return max(int(sheets), 0)
