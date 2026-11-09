"""Cost of cutting one press run."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

from backend.new_core import Cutter, CutterOperator
from backend.new_core.accountant.cost_report import CostReport
from backend.new_core.operations.cut.cut import Cut
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.values.money import Money


@dataclass(frozen=True, slots=True)
class CutPricing:
    """Prices cutter salary from stack lifts and imposition cuts."""

    cutter: Cutter
    operator: CutterOperator
    print_run: PrintRun

    def report(self) -> CostReport:
        stack = self._sheets_in_stack()
        lifts = (
            Decimal(self.print_run.imposition_count()) / Decimal(stack)
        ).to_integral_value(rounding=ROUND_CEILING)
        human_cuts = int(lifts) * self.print_run.imposition.cuts()
        work = (
            self.operator.salary_by_operation
            * human_cuts
            / self.print_run.imposition_count()
        )
        return CostReport(
            material=Money.zero(),
            work=work,
            startup=Money.zero(),
            markup=Money.zero(),
        )

    def _sheets_in_stack(self) -> int:
        sheets = (
            Decimal(self.cutter.max_stack)
            / self.print_run.imposition.thickness()
        ).to_integral_value(rounding=ROUND_CEILING)
        return max(int(sheets), 0)

    def run(self) -> PrintRun:
        return self.print_run
