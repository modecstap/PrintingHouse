from _decimal import Decimal

from models.press_sheet import PressSheet
from stages.i_stage import IStage

METRE_COEFFICIENT = 1_000_000
KILO_COEFFICIENT = 1000


class PaperStage(IStage):

    def __init__(
            self,
            previous_stage: IStage,
            press_sheet: PressSheet,
            kilograms_paper_cost: Decimal,
            density: int
    ):
        self._previous_stage = previous_stage
        self._density = density
        self._kilograms_paper_cost = kilograms_paper_cost
        self._press_sheet = press_sheet

        self._paper_cost = Decimal(0)

        self._calculate_paper_cost()

    def get_cost(self) -> Decimal:
        return self._previous_stage.get_cost() + self._kilograms_paper_cost

    def get_cost_price(self) -> Decimal:
        return self._previous_stage.get_cost_price() + self._kilograms_paper_cost

    def _calculate_paper_cost(self):
        paper_area_mm2 = Decimal(self._press_sheet.width * self._press_sheet.height)
        paper_area_m2 = paper_area_mm2 / METRE_COEFFICIENT
        price_square_millimeter = self._kilograms_paper_cost / KILO_COEFFICIENT * self._density
        self._paper_cost = paper_area_m2 * price_square_millimeter
