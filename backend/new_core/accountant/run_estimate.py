"""Value object: one run's list of operation pricing strategies."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from backend.new_core.accountant.cost_report import CostReport
from backend.new_core.accountant.pricing_strategy import PricingStrategy
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.values.percent import Percent


@dataclass(frozen=True, slots=True)
class RunEstimate:
    """Pricing strategies for one print run, with a single validated press run."""

    _strategies: tuple[PricingStrategy, ...]
    _run: PrintRun
    _parts_markup: Percent = Percent(0)

    @classmethod
    def create(
            cls,
            strategies: Sequence[PricingStrategy],
            *,
            run: PrintRun | None = None,
            parts_markup: Percent = Percent(0),
    ) -> RunEstimate:
        """Builds an estimate from strategies and optionally pins the run.

        :raises ValueError: if strategies disagree on the run, or both are empty
        and no run is given.

        :return: a run estimate that implements :class:`RunEstimateView`.
        """
        if strategies:
            resolved = strategies[0].run()
            for strategy in strategies[1:]:
                if strategy.run().id != resolved.id:
                    raise ValueError("All estimates must be for the same run.")
        elif run is None:
            raise ValueError("Run estimate needs strategies or an explicit run.")
        else:
            resolved = run

        return cls(
            _strategies=tuple(strategies),
            _run=resolved,
            _parts_markup=parts_markup,
        )

    def aggregated_operations(self) -> CostReport:
        report = CostReport.zero()
        for strategy in self._strategies:
            report += strategy.report()
        return report

    def block_markup(self) -> Percent:
        return self._parts_markup

    def imposition_count(self) -> int:
        return self._run.imposition_count()

    def targets_on_imposition(self) -> int:
        return self._run.block.imposition.count()

    def block_count(self) -> int:
        return self._run.block.count
