from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

from backend.core.accountant.money import Money
from backend.new_core.errors import InvalidInput
from backend.new_core.press_job import PressJob


@dataclass(frozen=True)
class Cutter:
    id: int
    max_stack: int

    def __post_init__(self) -> None:
        """Rejects a negative stack height.

        :raises InvalidInput: if max_stack is below zero.

        :return: nothing. A stack height of zero stays.
        """
        if self.max_stack < 0:
            raise InvalidInput(
                "cutter",
                f"высота стопы меньше 0, высота={self.max_stack} мм",
            )


@dataclass(frozen=True)
class CutterOperator:
    id: int
    salary_by_operation: Money


def sheets_in_stack(max_stack: int, density: int) -> int:
    """Returns how many press sheets fit in one cutter stack.

    :param max_stack: the cutter stack height in millimetres.
    :param density: the density of the press sheet paper.
    A density of zero is rejected before this function runs.

    :return: max_stack * 1200 / density, rounded up to an integer,
    then raised to zero when that integer is negative.
    """
    sheets = (
        Decimal(max_stack) * Decimal(1200) / Decimal(density)
    ).to_integral_value(rounding=ROUND_CEILING)
    return max(int(sheets), 0)


@dataclass(frozen=True)
class Cut:
    cutter: Cutter
    operator: CutterOperator

    def material_price(self, job: PressJob) -> Money:
        """Returns no material for a cut.

        :param job: present for the shared operation signature. It is not used.

        :return: zero.
        """
        return Money.zero()

    def work_price(self, job: PressJob) -> Money:
        """Returns the cutter salary for one press sheet.

        :param job: the run whose sheet count, cut count, and paper density
        set the human cuts. The press sheet count and the sheets in a stack
        are already positive.

        :return: the salary times the human cuts, divided by the press sheet
        count. Human cuts are the stack lifts times the cut count. A lift
        count is the press sheet count divided by the sheets in a stack,
        rounded up.
        """
        stack = sheets_in_stack(
            self.cutter.max_stack,
            job.press_sheet.paper.density,
        )
        lifts = (
            Decimal(job.press_sheet_count) / Decimal(stack)
        ).to_integral_value(rounding=ROUND_CEILING)
        human_cuts = int(lifts) * job.cut_count
        return self.operator.salary_by_operation * human_cuts / job.press_sheet_count

    def startup_price(self, job: PressJob) -> Money:
        """Returns no startup for a cut.

        :param job: present for the shared operation signature. It is not used.

        :return: zero.
        """
        return Money.zero()
