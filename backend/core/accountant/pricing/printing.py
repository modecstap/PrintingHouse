from backend.core.accountant.money import Money
from backend.core.accountant.pricing.calculatable import Calculatable
from backend.core.accountant.pricing.stage_cost import StageCost
from backend.core.workplaces.printing.models import PrintingReport


class PrintingCalculation(Calculatable):
    def __init__(
            self,
            cyan: Money,
            magenta: Money,
            yellow: Money,
            black: Money,
            salary: Money,
        ):
        """Remembers the ink rates and the salary rate.

        Paper is not a stored rate. attach receives it for one calculation.

        :param cyan:
        :param magenta:
        :param yellow:
        :param black:
        :param salary:
        """
        self._report = None
        self._paper = None
        self._cyan = cyan
        self._magenta = magenta
        self._yellow = yellow
        self._black = black
        self._salary = salary

    @property
    def cyan(self) -> Money:
        """Returns the cyan rate passed to the constructor."""
        return self._cyan

    @property
    def magenta(self) -> Money:
        """Returns the magenta rate passed to the constructor."""
        return self._magenta

    @property
    def yellow(self) -> Money:
        """Returns the yellow rate passed to the constructor."""
        return self._yellow

    @property
    def black(self) -> Money:
        """Returns the black rate passed to the constructor."""
        return self._black

    @property
    def salary(self) -> Money:
        """Returns the salary rate passed to the constructor."""
        return self._salary

    def attach(
        self, report: PrintingReport, paper: Money
    ) -> "PrintingCalculation":
        """Attaches the printing report and the paper rate for this calculation.

        :param report:
        :param paper: the sheet rate, in rubles per kilogram.
        The rate is kept only on this calculation, the same way the report is.

        :raises RuntimeError:
        "Report is already attached" if the report is already attached.

        :return: this same object.
        """
        if self._report is not None:
            raise RuntimeError("Report is already attached")

        self._report = report
        self._paper = paper
        return self

    def calculate(self) -> StageCost:
        """Calculates ink, paper, and salary for one sheet's mass.

        :raises RuntimeError: "Report is not attach" if the report is not attached.

        :return: material_cost is the attached paper rate multiplied by
        report.mass_kg, plus ink. The mass is not multiplied by the run length.
        """
        if not self._report:
            raise RuntimeError("Report is not attach")

        paper = self._paper * self._report.mass_kg

        ink = Money.zero()
        cyan, magenta, yellow, black = self._report.used_ink
        total = (
                self._cyan * cyan +
                self._magenta * magenta +
                self._yellow * yellow +
                self._black * black
        )
        sheets = self._report.sheet_count
        if sheets != 0:
            ink = total / sheets

        salary = Money.zero()
        if self._report.human_operations != 0:
            salary = self._salary

        return StageCost(
            startup_cost=Money.zero(),
            material_cost=paper + ink,
            salary=salary,
        )
