from backend.core.accountant.money import Money
from backend.core.accountant.pricing.calculatable import Calculatable
from backend.core.accountant.pricing.stage_cost import StageCost
from backend.core.workplaces.cutting.models import CuttingReport


class CuttingCalculation(Calculatable):
    def __init__(self, salary: Money):
        """Remembers the cutting salary rate.

        :param salary:
        """
        self._report = None
        self._salary = salary

    @property
    def salary(self) -> Money:
        """Returns the salary rate passed to the constructor."""
        return self._salary

    def attach(
        self, report: CuttingReport, internal_sheet_count: int
    ) -> "CuttingCalculation":
        """Attaches the cutting report and the internal sheet count.

        :param report:
        :param internal_sheet_count:

        :raises RuntimeError:
        "Report is already attached" if the report is already attached.

        :return: this same object.
        """
        if self._report is not None:
            raise RuntimeError("Report is already attached")

        self._report = report
        self._internal_sheet_count = internal_sheet_count
        return self

    def calculate(self) -> StageCost:
        """Calculates the cutting startup, material, and salary before markup.

        :raises RuntimeError: "Report is not attach" if the report is not attached.
        :raises InvalidPriceException: if the amount is below zero.

        :return: startup and material are zero.
        Salary is the rate multiplied by human_cuts and divided by internal_sheet_count.
        Zero cuts give a zero salary by multiplication, with no separate branch.
        No rounding to a kopeck.
        """
        if not self._report:
            raise RuntimeError("Report is not attach")

        salary = (self._salary * self._report.human_cuts) / self._internal_sheet_count
        return StageCost(
            startup_cost=Money.zero(),
            material_cost=Money.zero(),
            salary=salary,
        )
