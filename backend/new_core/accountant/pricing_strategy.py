"""Protocol for operation cost estimation."""

from typing import Protocol

from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.accountant.cost_report import CostReport


__all__ = ["PricingStrategy"]

class PricingStrategy(Protocol):
    """Estimates the cost of one run operation."""

    def report(self) -> CostReport:
        """Returns material, work, startup, and markup for one press target.
"""
        ...

    def run(self) -> PrintRun:
        """Returns the print run associated with this pricing strategy.
"""
        ...
