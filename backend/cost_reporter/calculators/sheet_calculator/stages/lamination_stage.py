from _decimal import Decimal

from backend.cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage
from backend.models import Lamination


class LaminationStage(IStage):

    def __init__(
            self,
            previous_stage: IStage,
            lamination: Lamination,
            sheet_lamination_cost: Decimal,
            sheet_count: int
    ):
        self._previous_stage = previous_stage
        self._lamination = lamination
        self._sheet_lamination_cost = sheet_lamination_cost
        self._lamination_stage_cost = self._calculate_lamination_cost()

        initial_price = Decimal(200)/sheet_count

        # Стоимость алёнки примерно равна 1/2 от стоимости печати
        self._cost_price = (
                self._previous_stage.get_cost_price()
                + self._lamination_stage_cost / 2
                + initial_price
        )
        self._cost = (
                self._previous_stage.get_cost()
                + self._lamination_stage_cost
                + initial_price
        )

    def get_cost(self) -> Decimal:
        return self._cost

    def get_cost_price(self) -> Decimal:
        return self._cost_price

    def _calculate_lamination_cost(self) -> Decimal:
        if self._lamination == Lamination.DONT:
            return Decimal(0)
        if self._lamination == Lamination.ONE_ZERO:
            return self._sheet_lamination_cost
        if self._lamination == Lamination.ONE_ONE:
            return self._sheet_lamination_cost * 2
