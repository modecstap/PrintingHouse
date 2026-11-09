"""Cost of one print on a press target."""

from __future__ import annotations

from dataclasses import dataclass

from backend.new_core import Printer, PressOperator, Sheet
from backend.new_core.accountant.cost_report import CostReport
from backend.new_core.operations.print.chroma import Chroma
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.values.money import Money


@dataclass(frozen=True, slots=True)
class PrintPricing:
    """Prices one print from paper, ink, salary, and printer startup."""

    printer: Printer
    operator: PressOperator
    chroma: Chroma
    paper: Sheet
    print_run: PrintRun

    def report(self) -> CostReport:
        cyan, magenta, yellow, black = self.chroma.consumed_sheets()
        printer = self.printer
        ink = (
            printer.cyan * cyan
            + printer.magenta * magenta
            + printer.yellow * yellow
            + printer.black * black
        )
        material = self.paper.price() + ink
        if self.chroma is Chroma.ZERO_ZERO:
            work = Money.zero()
        else:
            work = self.operator.salary_by_operation

        return CostReport(
            material=material,
            work=work,
            startup=printer.startup / self.print_run.imposition_count(),
            markup=Money.zero(),
        )

    def run(self) -> PrintRun:
        return self.print_run
