"""Cost of one die cut on a press target."""

from __future__ import annotations

from dataclasses import dataclass

from backend.new_core import DieCutterOperator
from backend.new_core.accountant.cost_report import CostReport
from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.values.money import Money


@dataclass(frozen=True, slots=True)
class DieCutPricing:
    """Prices die cutting from operator salary only."""

    operator: DieCutterOperator
    print_run: PrintRun

    def report(self) -> CostReport:
        return CostReport(
            material=Money.zero(),
            work=self.operator.salary_by_operation,
            startup=Money.zero(),
            markup=Money.zero(),
        )

    def run(self) -> PrintRun:
        return self.print_run
