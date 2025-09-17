import math
from decimal import Decimal, ROUND_HALF_UP

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
            unit_cost: Decimal,
            unit_cost_price: Decimal,
            markup: Decimal
    ):
        self._item_count = item_count
        self._item_per_sheet = item_per_sheet
        self._unit_cost = unit_cost
        self._unit_cost_price = unit_cost_price
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
            self._volume_base_markup = Decimal("1.3")
        elif self._sheet_count < 500:
            self._volume_base_markup = Decimal("1")
        else:
            self._volume_base_markup = Decimal("0.95")

    def _calculate_cost_price(self):
        self._cost_price = self._unit_cost_price * self._item_count

    def sheet_count(self) -> int:
        return self._sheet_count

    def _calculate_cost(self):
        self._cost = self._unit_cost * self._item_count * self._volume_base_markup

    def cost(self) -> Decimal:
        return self._cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def cost_price(self) -> Decimal:
        return self._cost_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
