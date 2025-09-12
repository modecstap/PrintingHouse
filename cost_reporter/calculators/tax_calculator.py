from decimal import Decimal


class TaxCalculator:
    """
    Рассчитывает стоимость тиража с учётом налогов.
    """

    def __init__(self, tax_rate: Decimal, cost_before_tax: Decimal):
        self._tax_rate = tax_rate
        self._cost_before_tax = cost_before_tax

        self._cost_after_tax = Decimal(0)

        self._calculate_cost()

    def cost_after_tax(self) -> Decimal:
        return self._cost_after_tax

    def cost_before_tax(self) -> Decimal:
        return self._cost_before_tax

    def _calculate_cost(self):
        self._cost_after_tax = self._cost_before_tax * self._tax_rate
