"""Protocol for operation cost estimation."""

from typing import Protocol

from backend.new_core import PrintRun
from backend.new_core.accountant.cost_report import CostReport


class PricingStrategy(Protocol):
    """Estimates the cost of one run operation."""

    def report(self) -> CostReport:
        """Returns material, work, startup, and markup for one press target."""
        ...

    def run(self) -> PrintRun:
        """Returns the print run associated with this pricing strategy."""
        ...
