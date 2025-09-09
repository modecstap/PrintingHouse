from cost_calculator import CostCalculator
from models.cost_report import CostReport
from profit_calculator import ProfitCalculator
from sheet_calculator import SheetCalculator


class CostReporter:
    """Оркестратор: агрегирует расчёты в отчёт"""

    def __init__(
        self,
        sheet_calc: SheetCalculator,
        cost_calc: CostCalculator,
        profit_calc: ProfitCalculator,
    ):
        self._sheet_calc = sheet_calc
        self._cost_calc = cost_calc
        self._profit_calc = profit_calc

    def get_report(self) -> CostReport:
        items_per_sheet = self._sheet_calc.items_per_sheet()
        sheet_count = self._sheet_calc.sheet_count()
        sheet_cost = self._sheet_calc.sheet_cost()
        cut_price = self._sheet_calc.cut_price()

        unit_cost = self._cost_calc.unit_cost(sheet_cost, cut_price)
        edition_cost = self._cost_calc.edition_cost(sheet_count, unit_cost)

        profit_before_tax = self._profit_calc.profit_before_tax(edition_cost)
        profit_after_tax = self._profit_calc.profit_after_tax(profit_before_tax)

        return CostReport(
            items_per_sheet=items_per_sheet,
            sheet_count=sheet_count,
            unit_cost_price=sheet_cost,
            unit_cost=unit_cost,
            edition_cost=edition_cost,
            profit_before_tax=profit_before_tax,
            profit_after_tax=profit_after_tax,
        )

    