from decimal import Decimal

from cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage


class EmptyStage(IStage):
    def get_cost(self) -> Decimal:
        return Decimal(0)

    def get_cost_price(self) -> Decimal:
        return Decimal(0)
