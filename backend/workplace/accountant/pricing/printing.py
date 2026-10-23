from backend.workplace.accountant.money import Money
from backend.workplace.accountant.pricing.calculatable import Calculatable
from backend.workplace.accountant.pricing.stage_cost import StageCost
from backend.workplace.workplaces.printing.models import PrintingReport


class PrintingCalculation(Calculatable):
    def __init__(
            self,
            cyan: Money,
            magenta: Money,
            yellow: Money,
            black: Money,
            paper: Money,
            salary: Money,
        ):
        self._report = None
        self._cyan = cyan
        self._magenta = magenta
        self._yellow = yellow
        self._black = black
        self._paper = paper
        self._salary = salary

    def attach(self, report: PrintingReport) -> "PrintingCalculation":
        if self._report is not None:
            raise RuntimeError("Report is already attached")

        self._report = report
        return self

    def calculate(self) -> StageCost:
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
