import math
from decimal import Decimal

from item_placement_calculator.placement_optimizer import PlacementOptimizer
from models.edition import Edition
from models.production import Production

METRE_COEFFICIENT = 1_000_000


class SheetCalculator:
    """Отвечает за расчёт параметров печатного листа"""

    def __init__(self, edition: Edition, production: Production):
        self._edition = edition
        self._production = production

        self._placement = PlacementOptimizer(
            press_sheet=self._production.press_sheet,
            list_size=self._edition.list_size
        )

    def items_per_sheet(self) -> int:
        return self._placement.get_items_per_sheet()

    def sheet_count(self) -> int:
        return math.ceil(self._edition.count / self._placement.get_cut_count())

    def sheet_cost(self) -> Decimal:
        press_sheet = self._production.press_sheet
        paper_area_m2 = (press_sheet.width * press_sheet.height) / METRE_COEFFICIENT
        paper_cost = paper_area_m2 * self._production.paper_cost * self._edition.density
        return paper_cost + self._production.ink_cost

    def cut_price(self) -> Decimal:
        return self._placement.get_cut_count() * self._production.cutting_cost