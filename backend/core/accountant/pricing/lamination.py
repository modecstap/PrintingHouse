from backend.core.accountant.money import Money
from backend.core.accountant.pricing.calculatable import Calculatable
from backend.core.accountant.pricing.stage_cost import StageCost
from backend.core.workplaces.lamination.models import LaminationReport


class LaminationCalculation(Calculatable):
    def __init__(self, startup: Money, film_cost: Money, salary: Money):
        """Remembers the startup, film, and salary rates.

        :param startup:
        :param film_cost:
        :param salary:
        """
        self._report = None
        self._startup = startup
        self._film_cost = film_cost
        self._salary = salary

    @property
    def startup(self) -> Money:
        """Returns the startup rate passed to the constructor."""
        return self._startup

    @property
    def film_cost(self) -> Money:
        """Returns the film_cost rate passed to the constructor."""
        return self._film_cost

    @property
    def salary(self) -> Money:
        """Returns the salary rate passed to the constructor."""
        return self._salary

    def attach(
        self, report: LaminationReport, internal_sheet_count: int
    ) -> "LaminationCalculation":
        """Attaches the lamination report and the internal sheet count.

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
        """Calculates the lamination startup, material, and salary before markup.

        :raises RuntimeError: "Report is not attach" if the report is not attached.
        :raises InvalidPriceException: if the amount is below zero.

        :return: when film_sides is 0, StageCost.zero().
        Otherwise startup is the startup rate divided by internal_sheet_count.
        Material is film_cost multiplied by film_sides. Salary equals the salary rate
        and is not multiplied by film_sides again. Startup is taken from the rate,
        with no separate count in the calculation. No rounding to a kopeck.
        """
        if not self._report:
            raise RuntimeError("Report is not attach")

        if self._report.film_sides == 0:
            return StageCost.zero()

        return StageCost(
            startup_cost=self._startup / self._internal_sheet_count,
            material_cost=self._film_cost * self._report.film_sides,
            salary=self._salary,
        )
