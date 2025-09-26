from decimal import Decimal, ROUND_HALF_UP

from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_strategies.pacement_strategy import \
    PlacementStrategy
from backend.cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage


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
        self._sheet_cost_price = self._cost_calculator.get_cost_price()
        self._sheet_cost = self._cost_calculator.get_cost()

    def items_per_sheet(self) -> int:
        return self._items_per_sheet

    def get_cost_price(self) -> Decimal:
        return self._sheet_cost_price.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def get_cost(self) -> Decimal:
        return self._sheet_cost.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
