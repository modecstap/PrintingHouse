from backend.core.accountant.money import Money
from backend.core.accountant.pricing.calculatable import Calculatable
from backend.core.accountant.pricing.stage_cost import StageCost
from backend.core.workplaces.die_cutting.models import DieCuttingReport


class DieCuttingCalculation(Calculatable):
    def __init__(self, salary: Money):
        """Remembers the die-cutting salary rate.

        :param salary:
        """
        self._report = None
        self._salary = salary

    @property
    def salary(self) -> Money:
        """Returns the salary rate passed to the constructor."""
        return self._salary

    def attach(self, report: DieCuttingReport) -> "DieCuttingCalculation":
        """Attaches the die-cutting report.

        :param report:

        :raises RuntimeError:
        "Report is already attached" if the report is already attached.

        :return: this same object.
        """
        if self._report is not None:
            raise RuntimeError("Report is already attached")

        self._report = report
        return self

    def calculate(self) -> StageCost:
        """Calculates the die-cutting startup, material, and salary before markup.

        :raises RuntimeError: "Report is not attach" if the report is not attached.
        :raises InvalidPriceException: if the amount is below zero.

        :return: when sheet_count is 0, StageCost.zero(). Otherwise startup
        and material are zero, and the salary equals the rate once.
        No rounding to a kopeck.
        """
        if not self._report:
            raise RuntimeError("Report is not attach")

        if self._report.sheet_count == 0:
            return StageCost.zero()

        return StageCost(
            startup_cost=Money.zero(),
            material_cost=Money.zero(),
            salary=self._salary,
        )
