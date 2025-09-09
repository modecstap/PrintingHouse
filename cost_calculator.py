from decimal import Decimal


class CostCalculator:
    """Отвечает за расчёт себестоимости"""

    @staticmethod
    def unit_cost(sheet_cost: Decimal, cut_price: Decimal) -> Decimal:
        return sheet_cost + cut_price

    @staticmethod
    def edition_cost(sheet_count: int, unit_cost: Decimal) -> Decimal:
        return sheet_count * unit_cost