from decimal import Decimal

from cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage
from cost_reporter.models.edition import Chroma


class InkStage(IStage):

    def __init__(
            self,
            previous_stage: IStage,
            color_ink_cost: Decimal,
            black_ink_cost: Decimal,
            chroma: Chroma
    ):
        self._previous_stage = previous_stage
        self._color_ink_cost = color_ink_cost
        self._black_ink_cost = black_ink_cost
        self._chroma = chroma
        self._ink_cost = Decimal(0)

        self._calculate_ink_cost()

        self._cost_price = self._previous_stage.get_cost_price() + self._ink_cost
        self._cost = self._previous_stage.get_cost() + self._ink_cost

    def get_cost(self) -> Decimal:
        return self._cost

    def get_cost_price(self) -> Decimal:
        return self._cost_price

    def _calculate_ink_cost(self):
        if self._chroma == Chroma.ONE_ZERO:
            self._ink_cost = self._black_ink_cost
        elif self._chroma == Chroma.ONE_ONE:
            self._ink_cost = self._black_ink_cost * 2
        elif self._chroma == Chroma.FOUR_ZERO:
            self._ink_cost = self._color_ink_cost
        elif self._chroma == Chroma.FOUR_FOUR:
            self._ink_cost = self._color_ink_cost * 2
