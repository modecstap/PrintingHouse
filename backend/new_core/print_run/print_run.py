"""One press run for a block, and the operations appended to it."""

from __future__ import annotations

from decimal import ROUND_CEILING, Decimal

from backend.new_core.accountant.percent import Percent
from backend.new_core.part import Part
from backend.new_core.errors import InvalidInput
from backend.new_core.print_run.imposition import Imposition
from backend.new_core.operations.cut.cut import Cut
from backend.new_core.operations.cut.cutter import Cutter
from backend.new_core.operations.cut.cutter_operator import CutterOperator
from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.operations.die_cut.die_cutter_operator import DieCutterOperator
from backend.new_core.operations.laminate.laminate import Laminate
from backend.new_core.operations.laminate.laminator import Laminator
from backend.new_core.operations.laminate.laminator_operator import LaminatorOperator
from backend.new_core.operations.print.press_operator import PressOperator
from backend.new_core.operations.print.print import Print
from backend.new_core.operations.print.printer import Printer
from backend.new_core.operations.print.print_specification import PrintSpecification
from backend.new_core.operations.run_operation import RunOperation


_WASTE_ALLOWANCE = Percent(3)


class PrintRun:
    """A run that prints one block and records the operations it uses."""

    def __init__(
            self,
            id: int,  # pylint: disable=redefined-builtin
            for_order: int,
            block: Part,
            required_count: int,
            imposition: Imposition,
    ) -> None:
        self.id = id
        self.block = block
        self.for_order = for_order
        self.required_count = required_count
        self.imposition = imposition
        self.operations: list[RunOperation] = []

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

        :return: required_count times a 3 percent waste allowance, divided
        by the number of target sheets on one press sheet, rounded up
        to an integer.
        """
        sheets = (
                Decimal(self.required_count)
                * _WASTE_ALLOWANCE.factor()
                / Decimal(self.imposition.count())
        ).to_integral_value(rounding=ROUND_CEILING)
        return int(sheets)

    def print(
        self,
        printer: Printer,
        operator: PressOperator,
    ) -> Print:
        """Appends a print to this run.

        A second call appends a second print. Chroma comes from the block.
        Paper comes from the imposition.

        :param printer: the printer and its ink and startup prices.
        :param operator: the press operator and the salary.

        :return: the print already appended.
        """
        printing = Print(
            spec=PrintSpecification(
                chroma=self.block.chroma,
                paper=self.imposition.press_sheet,
            ),
            printer=printer,
            operator=operator,
        )
        self.operations.append(printing)
        return printing

    def laminate(
        self,
        laminator: Laminator,
        operator: LaminatorOperator,
    ) -> Laminate:
        """Appends a lamination to this run.

        The lamination and the film come from the block.

        :param laminator: the laminator and its startup price.
        :param operator: the laminator operator and the salary.

        :return: the lamination already appended.
        """
        laminate = Laminate(
            spec=self.block.lamination,
            laminator=laminator,
            operator=operator,
        )
        self.operations.append(laminate)
        return laminate

    def cut(self, cutter: Cutter, operator: CutterOperator) -> Cut:
        """Appends a cut to this run.

        :param cutter: the cutter and its stack height.
        :param operator: the cutter operator and the salary.

        :return: the cut already appended. It uses the imposition and
        the press sheet count of this run.
        """
        cut = Cut(
            cutter=cutter,
            operator=operator,
            imposition=self.imposition,
            sheet_count=self.press_sheet_count(),
        )
        self.operations.append(cut)
        return cut

    def die_cut(self, operator: DieCutterOperator) -> DieCut:
        """Appends a die cut to this run.

        :param operator: the die cutter operator and the salary.

        :return: the die cut already appended.
        """
        die_cut = DieCut(operator=operator)
        self.operations.append(die_cut)
        return die_cut
