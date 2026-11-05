from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal
from typing import TYPE_CHECKING

from backend.new_core import Block
from backend.new_core.errors import InvalidInput
from backend.new_core.print_run.imposition import Imposition
from backend.new_core.print_run.run_operation import RunOperation

if TYPE_CHECKING:
    from backend.core.workplaces.lamination.models import Lamination
    from backend.core.workplaces.printing.models import Chroma
    from backend.new_core.operations.cutting import Cut, Cutter, CutterOperator
    from backend.new_core.operations.die_cutting import DieCut, DieCutterOperator
    from backend.new_core.operations.lamination import (
        Film,
        Laminate,
        Laminator,
        LaminatorOperator,
    )
    from backend.new_core.operations.printing import PressOperator, Print, Printer


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

        # Not a dataclass field: Print.print_run points at this run, and a
        # field would cycle eq, hash, and repr.
        object.__setattr__(self, "_operations", [])

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

    def operations(self) -> tuple[RunOperation, ...]:
        """Returns the operations this run's factories appended.

        The order follows the factory calls, from the first to the last.
        A new run returns an empty tuple. An operation built by its own
        constructor is absent.

        :return: the appended operations, from the first factory call to
        the last.
        """
        return tuple(self._operations)

    def add_print(
        self,
        chroma: Chroma,
        printer: Printer,
        operator: PressOperator,
    ) -> Print:
        """Appends a print to this run.

        A second call appends a second print.

        :param chroma: the ink layout of the print.
        :param printer: the printer and its ink and startup prices.
        :param operator: the press operator and the salary.

        :return: the print already appended, whose print_run is this run.
        """
        from backend.new_core.operations.printing import Print

        printing = Print(
            chroma=chroma,
            printer=printer,
            operator=operator,
            print_run=self,
        )
        self._operations.append(printing)
        return printing

    def add_laminate(
        self,
        lamination: Lamination,
        laminator: Laminator,
        film: Film,
        operator: LaminatorOperator,
    ) -> Laminate:
        """Appends a lamination to this run.

        :param lamination: which film sides to apply.
        :param laminator: the laminator and its startup price.
        :param film: the film and its price.
        :param operator: the laminator operator and the salary.

        :return: the lamination already appended, whose print_run is this run.
        """
        from backend.new_core.operations.lamination import Laminate

        laminate = Laminate(
            lamination=lamination,
            laminator=laminator,
            film=film,
            operator=operator,
            print_run=self,
        )
        self._operations.append(laminate)
        return laminate

    def add_cut(self, cutter: Cutter, operator: CutterOperator) -> Cut:
        """Appends a cut to this run.

        :param cutter: the cutter and its stack height.
        :param operator: the cutter operator and the salary.

        :return: the cut already appended, whose print_run is this run.
        """
        from backend.new_core.operations.cutting import Cut

        cut = Cut(cutter=cutter, operator=operator, print_run=self)
        self._operations.append(cut)
        return cut

    def add_die_cut(self, operator: DieCutterOperator) -> DieCut:
        """Appends a die cut to this run.

        :param operator: the die cutter operator and the salary.

        :return: the die cut already appended. It has no print_run field.
        """
        from backend.new_core.operations.die_cutting import DieCut

        die_cut = DieCut(operator=operator)
        self._operations.append(die_cut)
        return die_cut
