from collections.abc import Sequence
from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

from backend.core.accountant.money import Money
from backend.new_core.cutting import Cut, sheets_in_stack
from backend.new_core.errors import InvalidInput
from backend.new_core.imposition import Imposition
from backend.new_core.order import Block
from backend.new_core.press_job import PressJob, RunOperation
from backend.new_core.report import CostReport


def _items_per_sheet(imposition: Imposition) -> int:
    item_count = imposition.count()
    if item_count <= 0:
        raise InvalidInput(
            "imposition",
            f"на печатный лист влезает {item_count} целевых листов",
        )
    return item_count


def _press_sheet_count(required_count: int, items_per_sheet: int) -> int:
    sheets = (
        Decimal(required_count)
        * Decimal(103)
        / Decimal(100)
        / Decimal(items_per_sheet)
    ).to_integral_value(rounding=ROUND_CEILING)
    return int(sheets)


@dataclass(frozen=True)
class PrintRun:
    id: int
    block: Block
    required_count: int
    imposition: Imposition

    def __post_init__(self) -> None:
        """Rejects a negative required count.

        :raises InvalidInput: if required_count is below zero.

        :return: nothing. A required count of zero stays.
        """
        if self.required_count < 0:
            raise InvalidInput(
                "print_run",
                f"необходимое количество меньше 0, количество={self.required_count}",
            )

    def production_count(self) -> int:
        """Returns how many target sheets the run produces.

        :raises InvalidInput: if a cell side is zero, or if the press
        sheet fits no positive number of target sheets.

        :return: the press sheet count times the sheets on one press
        sheet. A required count of zero with a positive grid returns zero.
        """
        items_per_sheet = _items_per_sheet(self.imposition)
        return (
            _press_sheet_count(self.required_count, items_per_sheet)
            * items_per_sheet
        )

    def cost_report(self, operations: Sequence[RunOperation]) -> CostReport:
        """Returns the eight money fields of this run.

        :param operations: the run operations, in the order they are added.
        An operation left out of this sequence adds nothing.

        :raises InvalidInput: on the first failed check, in this order.
        A cell side is zero. The press sheet fits no positive number of
        target sheets. The press sheet count is not positive. The press
        sheet paper density is zero. A passed cut fits no positive number
        of sheets in a stack.

        :return: the press-sheet material, startup, work, and their sum,
        plus those three parts divided by the smaller of the grid count
        and the required count. The target total is the sum of the three
        target parts.
        """
        items_per_sheet = _items_per_sheet(self.imposition)
        press_sheet_count = _press_sheet_count(
            self.required_count,
            items_per_sheet,
        )
        if press_sheet_count <= 0:
            raise InvalidInput(
                "print_run",
                "печатных листов 0, "
                f"необходимое количество={self.required_count}",
            )

        density = self.imposition.press_sheet.paper.density
        if density == 0:
            raise InvalidInput("paper", "плотность равна 0")

        for operation in operations:
            if isinstance(operation, Cut):
                stack = sheets_in_stack(operation.cutter.max_stack, density)
                if stack <= 0:
                    raise InvalidInput(
                        "cut",
                        "листов в стопе 0, "
                        f"высота стопы={operation.cutter.max_stack} мм, "
                        f"плотность={density}",
                    )

        job = PressJob(
            press_sheet_count=press_sheet_count,
            cut_count=self.imposition.cuts(),
            press_sheet=self.imposition.press_sheet,
        )
        material = Money.zero()
        startup = Money.zero()
        work = Money.zero()
        for operation in operations:
            material += operation.material_price(job)
            startup += operation.startup_price(job)
            work += operation.work_price(job)

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
