from backend.cost_reporter.calculators.edition_calculator import EditionCalculator
from backend.cost_reporter.calculators.item_calculator import ItemCalculator
from backend.cost_reporter.calculators.sheet_calculator.sheet_calculator import SheetCalculator
from backend.cost_reporter.calculators.tax_calculator import TaxCalculator
from backend.models.printing_cost_report import PrintingCostReport


class PrintingCostReporter:
    """Оркестратор: агрегирует расчёты в отчёт"""

    def __init__(
            self,
            sheet_calculator: SheetCalculator,
            item_calculator: ItemCalculator,
            edition_calculator: EditionCalculator,
            tax_calculator: TaxCalculator
    ):
        self._sheet_calc = sheet_calculator
        self._item_calculator = item_calculator
        self._edition_calculator = edition_calculator
        self._tax_calculator = tax_calculator

    def get_report(self) -> PrintingCostReport:
        items_per_sheet = self._sheet_calc.items_per_sheet()

        unit_cost_price = self._item_calculator.get_item_cost_price()
        unit_cost = self._item_calculator.get_item_cost()

        sheet_count = self._edition_calculator.sheet_count()
        edition_cost_price = self._edition_calculator.cost_price()
        edition_cost = self._edition_calculator.cost()

        profit_before_tax = self._tax_calculator.profit_before_tax()
        profit_after_tax = self._tax_calculator.profit_after_tax()

        return PrintingCostReport(
            items_per_sheet=items_per_sheet,
            sheet_count=sheet_count,
            unit_cost_price=unit_cost_price,
            unit_cost=unit_cost,
            edition_cost_price=edition_cost_price,
            edition_cost=edition_cost,
            profit_before_tax=profit_before_tax,
            profit_after_tax=profit_after_tax,
        )
