from _decimal import Decimal

from backend.cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage


class VolumeMarkupStage(IStage):
    def __init__(
            self,
            previous_stage: IStage,
            sheet_count: int
    ):
        self._previous_stage = previous_stage
        self._sheet_count = sheet_count

        self._calculate_volume_base_markup()

        self._cost_price = self._previous_stage.get_cost_price()
        self._cost = self._previous_stage.get_cost() * self._volume_base_markup

    def get_cost(self) -> Decimal:
        return self._cost

    def get_cost_price(self) -> Decimal:
        return self._cost_price

    def _calculate_volume_base_markup(self):
        if self._sheet_count < 5:
            self._volume_base_markup = Decimal("1.5")
        elif self._sheet_count < 100:
            self._volume_base_markup = Decimal("1.3")
        elif self._sheet_count < 500:
            self._volume_base_markup = Decimal("1")
        else:
            self._volume_base_markup = Decimal("0.95")
