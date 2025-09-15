import math
from decimal import Decimal

from backend.cost_reporter.calculators.exeptions.item_size_exception import ItemSizeException


class EditionCalculator:
    """
    Рассчитывает стоимость, себестоимость и количество печатных листов,
    необходимых для выполнения тиража.
    """

    def __init__(
            self,
            item_count: int,
            item_per_sheet: int,
            sheet_cost: Decimal,
            sheet_cost_price: Decimal,
            markup: Decimal
    ):
        self._item_count = item_count
        self._item_per_sheet = item_per_sheet
        self._sheet_cost = sheet_cost
        self._sheet_cost_price = sheet_cost_price
        self._markup = markup

        self._sheet_count = 0
        self._volume_base_markup = Decimal(0)
        self._cost = Decimal(0)
        self._cost_price = Decimal(0)

        self._calculate_sheet_count()
        self._calculate_volume_base_markup()
        self._calculate_cost_price()
        self._calculate_cost()

    def _calculate_sheet_count(self):
        try:
            sheet_count = self._item_count / self._item_per_sheet
        except ZeroDivisionError:
            raise ItemSizeException()
        self._sheet_count = math.ceil(sheet_count)

    def _calculate_volume_base_markup(self):
        if self._sheet_count < 5:
            self._volume_base_markup = Decimal("1.5")
        elif self._sheet_count < 100:
            self._volume_base_markup = Decimal("1.15")
        elif self._sheet_count < 500:
            self._volume_base_markup = Decimal("1.05")
        else:
            self._volume_base_markup = Decimal("1")

    def _calculate_cost_price(self):
        self._cost_price = self._sheet_cost_price * self._sheet_count

    def sheet_count(self) -> int:
        return self._sheet_count

    def _calculate_cost(self):
        self._cost = self._sheet_cost * self._sheet_count * self._volume_base_markup

    def cost(self) -> Decimal:
        return self._cost

    def cost_price(self) -> Decimal:
        return self._cost_price
