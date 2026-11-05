from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.core.workplaces.printing.models import Chroma
from backend.new_core import PrintRun

# One sheet, in the order cyan, magenta, yellow, black.
_INK_SHARES: dict[Chroma, tuple[int, int, int, int]] = {
    Chroma.ZERO_ZERO: (0, 0, 0, 0),
    Chroma.ONE_ZERO: (0, 0, 0, 1),
    Chroma.ONE_ONE: (0, 0, 0, 2),
    Chroma.FOUR_ZERO: (1, 1, 1, 1),
    Chroma.FOUR_ONE: (1, 1, 1, 2),
    Chroma.FOUR_FOUR: (2, 2, 2, 2),
}


@dataclass(frozen=True)
class Printer:
    id: int
    startup: Money
    cyan: Money
    magenta: Money
    yellow: Money
    black: Money


@dataclass(frozen=True)
class PressOperator:
    id: int
    salary_by_operation: Money


@dataclass(frozen=True)
class Print:
    chroma: Chroma
    printer: Printer
    operator: PressOperator
    print_run: PrintRun

    def material_price(self) -> Money:
        """Returns the paper and ink cost of one press sheet.

        :return: the press sheet price, plus each ink rate times the share
        of this chroma for one sheet.
        """
        cyan_share, magenta_share, yellow_share, black_share = _INK_SHARES[
            self.chroma
        ]
        ink = (
            self.printer.cyan * cyan_share
            + self.printer.magenta * magenta_share
            + self.printer.yellow * yellow_share
            + self.printer.black * black_share
        )
        return self.print_run.imposition.press_sheet.price() + ink

    def work_price(self) -> Money:
        """Returns the press operator salary for one press sheet.

        :return: the full salary when chroma is not ZERO_ZERO, otherwise zero.
        """
        if self.chroma is Chroma.ZERO_ZERO:
            return Money.zero()
        return self.operator.salary_by_operation

    def startup_price(self) -> Money:
        """Returns the printer startup spread over the press sheets.

        :return: the printer startup divided by the press sheet count.
        A chroma of ZERO_ZERO still divides the startup.
        """
        return self.printer.startup / self.print_run.press_sheet_count()
