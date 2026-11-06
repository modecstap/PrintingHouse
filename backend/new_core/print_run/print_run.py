from __future__ import annotations

from decimal import ROUND_CEILING, Decimal

from backend.new_core import Block
from backend.new_core.errors import InvalidInput
from backend.new_core.print_run.imposition import Imposition
from backend.new_core.operations.cutting import Cut, Cutter, CutterOperator
from backend.new_core.operations.die_cutting import DieCut, DieCutterOperator
from backend.new_core.operations.lamination import (
    Laminate,
    Laminator,
    LaminatorOperator,
)
from backend.new_core.operations.printing import (
    PressOperator,
    Print,
    Printer,
    PrintSpecification,
)
from backend.new_core.operations.run_operation import RunOperation


class PrintRun:
    def __init__(self, id: int, block: Block, required_count: int, imposition: Imposition) -> None:
        self.id = id
        self.block = block
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
