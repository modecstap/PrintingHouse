"""Read-only view of a priced print run."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.accountant.cost_report import CostReport
from backend.new_core.values.percent import Percent


class RunEstimateView(Protocol):
    """Exposes run totals for the accountant."""

    def aggregated_operations(self) -> CostReport:
        """Sums material, work, startup, and markup for one press target."""
        ...

    def block_markup(self) -> Percent:
        """Returns the block markup percent."""
        ...

    def imposition_count(self) -> int:
        """Returns how many press targets the run prints."""
        ...

    def targets_on_imposition(self) -> int:
        """Returns how many target sheets fit on one press target."""
        ...

    def block_count(self) -> int:
        """Returns the block copy count."""
        ...
