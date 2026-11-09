"""Cost of one lamination pass on a press target."""

from __future__ import annotations

from dataclasses import dataclass

from backend.new_core import Laminator, LaminatorOperator, Film
from backend.new_core.accountant.cost_report import CostReport
from backend.new_core.operations.laminate.lamination import Lamination
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.values.money import Money


@dataclass(frozen=True, slots=True)
class LaminatePricing:
    """Prices film, laminator startup, and operator salary."""

    laminator: Laminator
    operator: LaminatorOperator
    lamination: Lamination
    film: Film
    print_run: PrintRun

    def report(self) -> CostReport:
        sides = self.lamination.film_sides()
        if sides == 0:
            return CostReport.zero()
        return CostReport(
            material=self.film.price * sides,
            work=self.operator.salary_by_operation,
            startup=self.laminator.startup / self.print_run.imposition_count(),
            markup=Money.zero(),
        )

    def run(self) -> PrintRun:
        return self.print_run