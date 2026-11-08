"""One print of a press sheet."""

from dataclasses import dataclass

from backend.new_core.values.money import Money
from backend.new_core.operations.print.chroma import Chroma
from backend.new_core.operations.print.press_operator import PressOperator
from backend.new_core.operations.print.print_specification import PrintSpecification
from backend.new_core.operations.print.printer import Printer

# One sheet, in the order cyan, magenta, yellow, black.
_INK_SHARES: dict[Chroma, tuple[int, int, int, int]] = {
    Chroma.ZERO_ZERO: (0, 0, 0, 0),
    Chroma.ONE_ZERO: (0, 0, 0, 1),
    Chroma.ONE_ONE: (0, 0, 0, 2),
    Chroma.FOUR_ZERO: (1, 1, 1, 1),
    Chroma.FOUR_ONE: (1, 1, 1, 2),
    Chroma.FOUR_FOUR: (2, 2, 2, 2),
}


@dataclass(frozen=True, slots=True)
class Print:
    """
    Value Object. One print of a press sheet: the specification, the printer, and the operator.
    """

    spec: PrintSpecification

    printer: Printer
    operator: PressOperator

    def material_price(self) -> Money:
        """Returns the paper and ink cost of one press sheet.

        :return: the press sheet price, plus each ink rate times the share
        of this chroma for one sheet.
        """
        cyan_share, magenta_share, yellow_share, black_share = _INK_SHARES[
            self.spec.chroma
        ]
        ink = (
            self.printer.cyan * cyan_share
            + self.printer.magenta * magenta_share
            + self.printer.yellow * yellow_share
            + self.printer.black * black_share
        )
        return self.spec.paper_price() + ink

    def work_price(self) -> Money:
        """Returns the press operator salary for one press sheet.

        :return: the full salary when chroma is not ZERO_ZERO, otherwise zero.
        """
        if self.spec.chroma is Chroma.ZERO_ZERO:
            return Money.zero()
        return self.operator.salary_by_operation

    def startup_price(self) -> Money:
        """Returns the printer startup for the operation.

        :return: the printer startup. A chroma of ZERO_ZERO still returns
        the startup. The press sheet count does not divide it.
        """
        return self.printer.startup
