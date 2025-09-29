import math
from decimal import Decimal, ROUND_HALF_UP

from backend.cost_reporter.calculators.exeptions.item_size_exception import ItemSizeException

FITTING_COUNT = 2


class EditionCalculator:
    """
    Рассчитывает стоимость, себестоимость и количество печатных листов,
    необходимых для выполнения тиража.
    """

    def __init__(
            self,
            item_count: int,
            item_cost_price: Decimal,
            item_cost: Decimal,
            item_per_sheet: int,
    ):
        self._item_cost_price = item_cost_price
        self._item_cost = item_cost
        self._item_count = item_count
        self._item_per_sheet = item_per_sheet

        self._sheet_count = self._calculate_sheet_count()

    def _calculate_sheet_count(self) -> int:
        try:
            sheet_count = self._item_count / self._item_per_sheet
        except ZeroDivisionError:
            raise ItemSizeException()
        return math.ceil(sheet_count)

    def sheet_count(self) -> int:
        return self._sheet_count

    def cost(self) -> Decimal:
        return (self._item_count * self._item_cost).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def cost_price(self) -> Decimal:
        return (self._item_count * self._item_cost_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def profit(self) -> Decimal:
        return self.cost() - self.cost_price()
