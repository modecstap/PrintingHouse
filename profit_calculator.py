from decimal import Decimal

from models.edition import Edition
from models.production import Production


class ProfitCalculator:
    """Отвечает за расчёт прибыли"""

    def __init__(self, edition: Edition, production: Production):
        self._edition = edition
        self._production = production

    def profit_before_tax(self, edition_cost: Decimal) -> Decimal:
        income = edition_cost * self._edition.markup
        return income - edition_cost

    def profit_after_tax(self, profit_before_tax: Decimal) -> Decimal:
        return profit_before_tax * self._production.tax_rate