from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.core.workplaces.printing.models import Chroma
from backend.new_core.press_job import PressJob

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

    def material_price(self, job: PressJob) -> Money:
        """Returns the paper and ink cost of one press sheet.

        :param job: the press sheet whose mass is priced.
        The sheet count is not used.

        :return: the paper price per kilo times the sheet mass, plus each
        ink rate times the share of this chroma for one sheet.
        """
        paper = job.press_sheet.paper.price_per_kilo * job.press_sheet.mass_kg()
        cyan_share, magenta_share, yellow_share, black_share = _INK_SHARES[
            self.chroma
        ]
        ink = (
            self.printer.cyan * cyan_share
            + self.printer.magenta * magenta_share
            + self.printer.yellow * yellow_share
            + self.printer.black * black_share
        )
        return paper + ink

    def work_price(self, job: PressJob) -> Money:
        """Returns the press operator salary for one press sheet.

        :param job: present for the shared operation signature. It is not used.

        :return: the full salary when chroma is not ZERO_ZERO, otherwise zero.
        """
        if self.chroma is Chroma.ZERO_ZERO:
            return Money.zero()
        return self.operator.salary_by_operation

    def startup_price(self, job: PressJob) -> Money:
        """Returns the printer startup spread over the press sheets.

        :param job: the run whose press sheet count divides the startup.
        The count is already positive.

        :return: the printer startup divided by the press sheet count.
        A chroma of ZERO_ZERO still divides the startup.
        """
        return self.printer.startup / job.press_sheet_count
