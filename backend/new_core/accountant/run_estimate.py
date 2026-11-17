"""Value object: one run's list of operation pricing strategies."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from backend.new_core.accountant.cost_report import CostReport
from backend.new_core.accountant.pricing_strategy import PricingStrategy
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.values.percent import Percent


__all__ = ["RunEstimate"]


def _volume_factor(sheet_count: int) -> Percent:
    """Handles volume factor.

    :param sheet_count: the sheet count.

    :return: the Percent result.
    """
    if sheet_count < 5:
        return Percent(30)
    if sheet_count < 100:
        return Percent(15)
    if sheet_count < 500:
        return Percent(5)
    return Percent(0)


@dataclass(frozen=True, slots=True)
class RunEstimate:
    """Pricing strategies for one print run, with one validated press run."""

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

        :param strategies: the strategies.
        :param run: the run.
        :param parts_markup: the parts markup.

        :raises ValueError: if strategies disagree on the run, or both are empty

        :return: the RunEstimate result.
        """
        if strategies:
            resolved = strategies[0].run()
            for strategy in strategies[1:]:
                if strategy.run().id != resolved.id:
                    raise ValueError("All estimates must be for the same run.")
        elif run is None:
            raise ValueError(
                "Run estimate needs strategies or an explicit run.")
        else:
            resolved = run

        return cls(
            _strategies=tuple(strategies),
            _run=resolved,
            _parts_markup=parts_markup,
        )

    def sheet_report(self) -> CostReport:
        """Returns the operation cost of one press target with markups.

        :return: the CostReport result.
        """
        report = CostReport.zero()
        for strategy in self._strategies:
            report += strategy.report()
        report = report.apply_markup(self._parts_markup)
        volume_markup = _volume_factor(self._run.imposition_count())
        return report.apply_markup(volume_markup)

    def list_report(self) -> CostReport:
        """Returns the press-target cost divided across the target sheets.

        :return: the CostReport result.
        """
        return self.sheet_report() / self.targets_on_imposition()

    def block_report(self) -> CostReport:
        """Returns the per-target cost times the block sheet count.

        :return: the CostReport result.
        """
        return self.list_report() * self._run.block.count

    def targets_on_imposition(self) -> int:
        """Handles targets on imposition.

        :return: the int result.
        """
        return self._run.block.imposition.count()
