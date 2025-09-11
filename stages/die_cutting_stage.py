from _decimal import Decimal

from models.edition import Lamination
from stages.i_stage import IStage


class DieCuttingStage(IStage):

    def __init__(
            self,
            previous_stage: IStage,
            die_cutting: bool,
            die_cutting_cost: Decimal
    ):
        self._previous_stage = previous_stage
        self._die_cutting = die_cutting
        self._die_cutting_cost = die_cutting_cost

        self._die_cutting_price = Decimal(0)

        self._calculate_die_cutting_cost()

    def get_cost(self) -> Decimal:
        return self._previous_stage.get_cost() + self._die_cutting_price

    def get_cost_price(self) -> Decimal:
        return self._previous_stage.get_cost_price()

    def _calculate_die_cutting_cost(self):
        if self._die_cutting:
            self._die_cutting_price = self._die_cutting_cost
