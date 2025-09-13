from _decimal import Decimal

from cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage


class TaxCompensationStage(IStage):

    def __init__(
            self,
            previous_stage: IStage,
            tax_rate: Decimal
    ):
        self._previous_stage = previous_stage
        self._tax_rate = tax_rate

        self._cost_price = self._previous_stage.get_cost_price()
        self._cost = self._previous_stage.get_cost() / self._tax_rate

    def get_cost(self) -> Decimal:
        return self._cost

    def get_cost_price(self) -> Decimal:
        return self._cost_price
