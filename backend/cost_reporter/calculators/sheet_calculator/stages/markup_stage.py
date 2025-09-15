from _decimal import Decimal

from backend.cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage


class MarkupStage(IStage):

    def __init__(
            self,
            previous_stage: IStage,
            markup: Decimal
    ):
        self._previous_stage = previous_stage
        self._markup = markup

        self._cost_price = self._previous_stage.get_cost_price()
        self._cost = self._previous_stage.get_cost() * self._markup

    def get_cost(self) -> Decimal:
        return self._cost

    def get_cost_price(self) -> Decimal:
        return self._cost_price
