from decimal import Decimal

from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_strategies.pacement_strategy import \
    PlacementStrategy
from backend.cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage


class CutStage(IStage):

    def __init__(
            self,
            previous_stage: IStage,
            cut_cost: Decimal,
            placement: PlacementStrategy
    ):
        self._previous_stage = previous_stage
        self._cut_cost = cut_cost
        self._placement = placement

        self._die_cut_price = Decimal(0)

        self._calculate_cut_price()

        self._cost_price = self._previous_stage.get_cost_price()
        self._cost = self._previous_stage.get_cost() + self._die_cut_price

    def get_cost(self) -> Decimal:
        return self._cost

    def get_cost_price(self) -> Decimal:
        return self._cost_price

    def _calculate_cut_price(self):
        self._cutting_price = self._placement.get_cut_count() * self._cut_cost
