from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

from backend.core.accountant.money import Money
from backend.new_core import Imposition
from backend.new_core.errors import InvalidInput


@dataclass(frozen=True)
class Cutter:
    id: int
    max_stack: int

    def __post_init__(self) -> None:
        """Rejects a stack height that is not positive.

        :raises InvalidInput: if max_stack is below zero, or if it is zero
        after a negative height is rejected.

        :return: nothing.
        """
        if self.max_stack < 0:
            raise InvalidInput(
                "cutter",
                f"высота стопы меньше 0, высота={self.max_stack} мм",
            )
        if self.max_stack == 0:
            raise InvalidInput(
                "cutter",
                f"высота стопы равна 0, высота={self.max_stack} мм",
            )


@dataclass(frozen=True)
class CutterOperator:
    id: int
    salary_by_operation: Money


@dataclass(frozen=True, slots=True)
class Cut:
    """
    Value Object. One cut of a run: the cutter, the operator, the imposition, and the press-sheet count.
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
