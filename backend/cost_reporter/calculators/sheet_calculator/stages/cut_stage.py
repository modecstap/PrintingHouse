import math
from decimal import Decimal

from backend.cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage


class CutStage(IStage):

    def __init__(
            self,
            previous_stage: IStage,
            cut_cost: Decimal,
            cut_count: int,
            sheet_count: int,
            sheet_in_stack: int
    ):
        self._previous_stage = previous_stage
        self._cut_cost = cut_cost
        self._cut_count = cut_count
        self._sheet_count = sheet_count
        self._sheet_in_stack = sheet_in_stack

        self._cutting_price = Decimal(0)

        self._calculate_cut_price()

        self._cost_price = self._previous_stage.get_cost_price()
        self._cost = self._previous_stage.get_cost() + self._cutting_price

    def get_cost(self) -> Decimal:
        return self._cost

    def get_cost_price(self) -> Decimal:
        return self._cost_price

    def _calculate_cut_price(self):
        cutman_salary = math.ceil(self._sheet_count / self._sheet_in_stack) * self._cut_count * self._cut_cost
        self._cutting_price = cutman_salary / self._sheet_count
