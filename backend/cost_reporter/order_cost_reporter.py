from decimal import Decimal, ROUND_HALF_UP

from backend.models import OrderCostReport, Operation, Economy, PrintingCostReport


class OrderCostReporter:
    def __init__(
            self,
            unit_count: int,
            printing_reports: list[PrintingCostReport],
            operations: list[Operation],
            economy: Economy
    ):
        self._unit_count = unit_count
        self._printing_reports = printing_reports
        self._operations = operations
        self._economy = economy

        self._printing_cost = Decimal("0")
        self._operation_cost = Decimal("0")
        self._operation_cost_price = Decimal("0")
        self._printing_cost_price = Decimal("0")

    def get_report(self) -> OrderCostReport:
        self._calculate_printings()
        self._calculate_operations()

        unit_cost_price = ((self._printing_cost_price+self._operation_cost_price)/self._unit_count)
        unit_cost_price = unit_cost_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        unit_cost = ((self._printing_cost+self._operation_cost)/self._unit_count)
        unit_cost = unit_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        edition_cost = unit_cost*self._unit_count

        profit_after_tax = edition_cost-unit_cost_price*self._unit_count

        return OrderCostReport(
            unit_cost_price=unit_cost_price,
            unit_cost=unit_cost,
            edition_cost=edition_cost,
            profit_after_tax=profit_after_tax,
            printing_cost_reports=self._printing_reports,
        )

    def _calculate_printings(self):
        for printing in self._printing_reports:
            self._printing_cost += printing.edition_cost
            self._printing_cost_price += printing.edition_cost_price

    def _calculate_operations(self):
        if not self._operations:
            return

        for operation in self._operations:
            self._operation_cost_price += operation.cost * self._unit_count
            total_markup = ((1 + self._economy.markup / 100) * (1 / self._economy.tax_rate))
            self._operation_cost += self._operation_cost_price * total_markup
