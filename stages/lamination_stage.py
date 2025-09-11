from _decimal import Decimal

from models.edition import Lamination
from stages.i_stage import IStage


class LaminationStage(IStage):

    def __init__(
            self,
            previous_stage: IStage,
            lamination: Lamination,
    ):
        self._previous_stage = previous_stage
        self._lamination = lamination

        self._lamination_cost = Decimal(0)

        self._calculate_lamination_cost()

    def get_cost(self) -> Decimal:
        return self._previous_stage.get_cost() + self._lamination_cost

    def get_cost_price(self) -> Decimal:
        return self._previous_stage.get_cost_price() + self._ink_cost

    def _calculate_lamination_cost(self):
        if self._lamination == Lamination.DONT:
            self._lamination_cost = 0
        if self._lamination == Lamination.ONE_ZERO:
            self._lamination_cost = self._production.lamination_cost
        if self._lamination == Lamination.ONE_ONE:
            self._lamination_cost = self._production.lamination_cost * 2