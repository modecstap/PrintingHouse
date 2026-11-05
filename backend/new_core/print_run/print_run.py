from collections.abc import Sequence
from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

from backend.core.accountant.money import Money
from backend.new_core import Block
from backend.new_core.errors import InvalidInput
from backend.new_core.print_run.imposition import Imposition
from backend.new_core.print_run.run_operation import RunOperation
from backend.new_core.print_run.report import CostReport


@dataclass(frozen=True)
class PrintRun:
    id: int
    block: Block
    required_count: int
    imposition: Imposition


    def __post_init__(self) -> None:
        """Rejects a run that prints no press sheets.

        :raises InvalidInput: if required_count is below zero. A cell side
        of zero, or a press sheet that fits no target sheets, is raised by
        the imposition while the press sheet count is calculated. A required
        count of zero raises the press sheet count error.

        :return: nothing.
        """
        if self.required_count < 0:
            raise InvalidInput(
                "print_run",
                f"необходимое количество меньше 0, количество={self.required_count}",
            )

        if self.press_sheet_count() <= 0:
            raise InvalidInput(
                "print_run",
                "печатных листов 0, "
                f"необходимое количество={self.required_count}",
            )

    def production_count(self) -> int:
        """Returns how many target sheets the run produces.

        :return: the press sheet count times the sheets on one press sheet.
        """
        return self.press_sheet_count() * self.imposition.count()

    def press_sheet_count(self) -> int:
        """Returns how many press sheets the run prints.

        :raises InvalidInput: if a cell side is zero, or if the press sheet
        fits no positive number of target sheets.

        :return: required_count times 103/100, divided by the number of
        target sheets on one press sheet, rounded up to an integer.
        """
        sheets = (
                Decimal(self.required_count)
                # TODO выделить проценты
                * Decimal(103)
                / Decimal(100)
                # ----------------------
                / Decimal(self.imposition.count())
        ).to_integral_value(rounding=ROUND_CEILING)
        return int(sheets)

    def cost_report(self, operations: Sequence[RunOperation]) -> CostReport:
        """Returns the eight money fields of this run.

        :param operations: the run operations, in the order they are added.
        An operation left out of this sequence adds nothing.

        :return: the press-sheet material, startup, work, and their sum,
        plus those three parts divided by the smaller of the grid count
        and the required count. The target total is the sum of the three
        target parts.
        """
        items_per_sheet = self.imposition.count()

        material = Money.zero()
        startup = Money.zero()
        work = Money.zero()
        for operation in operations:
            material += operation.material_price()
            startup += operation.startup_price()
            work += operation.work_price()

        press_sheet_total = material + startup + work
        divisor = min(items_per_sheet, self.required_count)
        target_material = material / divisor
        target_startup = startup / divisor
        target_work = work / divisor
        return CostReport(
            target_material=target_material,
            target_startup=target_startup,
            target_work=target_work,
            target_total=target_material + target_startup + target_work,
            press_sheet_material=material,
            press_sheet_startup=startup,
            press_sheet_work=work,
            press_sheet_total=press_sheet_total,
        )
