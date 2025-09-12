from _decimal import Decimal

from cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage
from cost_reporter.models.edition import Lamination


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

        self._cost_price = self._previous_stage.get_cost_price()
        self._cost = self._previous_stage.get_cost() + self._lamination_cost

    def get_cost(self) -> Decimal:
        return self._cost

    def get_cost_price(self) -> Decimal:
        return self._cost_price

    def _calculate_lamination_cost(self):
        if self._lamination == Lamination.DONT:
            self._lamination_cost = 0
        if self._lamination == Lamination.ONE_ZERO:
            self._lamination_cost = self._production.lamination_cost
        if self._lamination == Lamination.ONE_ONE:
            self._lamination_cost = self._production.lamination_cost * 2
