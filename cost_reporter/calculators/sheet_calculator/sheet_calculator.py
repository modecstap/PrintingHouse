import math
from decimal import Decimal

from cost_reporter.calculators.exeptions.item_size_exception import ItemSizeException
from cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_strategies.pacement_strategy import \
    PlacementStrategy
from cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage


class SheetCalculator:
    """Отвечает за расчёт параметров печатного листа"""

    def __init__(
            self,
            items_count: int,
            placement: PlacementStrategy,
            cost_calculator: IStage
    ):
        self._items_count = items_count
        self._placement = placement
        self._cost_calculator = cost_calculator

        self._items_per_sheet = self._placement.get_items_count()
        self._cost_price = self._cost_calculator.get_cost_price()
        self._cost = self._cost_calculator.get_cost()

    def items_per_sheet(self) -> int:
        return self._items_per_sheet

    def sheet_count(self) -> int:
        try:
            sheet_count = self._items_count / self._placement.get_items_count()
        except ZeroDivisionError:
            raise ItemSizeException()
        return math.ceil(sheet_count)

    def get_cost_price(self) -> Decimal:
        return self._cost_price

    def get_cost(self) -> Decimal:
        return self._cost

    def get_unit_cost_price(self) -> Decimal:
        return self._cost_price / self._items_per_sheet

    def get_unit_cost(self) -> Decimal:
        return self._cost / self._items_per_sheet
