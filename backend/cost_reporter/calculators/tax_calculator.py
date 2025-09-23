from decimal import Decimal


class TaxCalculator:
    """
    Рассчитывает стоимость тиража с учётом налогов.
    """

    def __init__(self, tax_rate: Decimal, profit_before_tax: Decimal):
        self._tax_rate = tax_rate
        self._profit_before_tax = profit_before_tax

        self._profit_after_tax = Decimal(0)

        self._calculate_profit()

    def profit_after_tax(self) -> Decimal:
        return self._profit_after_tax

    def profit_before_tax(self) -> Decimal:
        return self._profit_before_tax

    def _calculate_profit(self):
        self._profit_after_tax = self._profit_before_tax * self._tax_rate
