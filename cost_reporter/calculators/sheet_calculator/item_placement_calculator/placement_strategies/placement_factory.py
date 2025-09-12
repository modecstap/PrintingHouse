from cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_strategies.grid_by_height_placement import \
    GridByHeightPlacement
from cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_strategies.grid_by_width_placement import \
    GridByWidthPlacement
from cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_strategies.pacement_strategy import \
    PlacementStrategy
from cost_reporter.models.list_size import ListSize
from cost_reporter.models.press_sheet import PressSheet


class PlacementFactory:
    def __init__(self, press_sheet: PressSheet, list_size: ListSize):
        self.press_sheet = press_sheet
        self.list_size = list_size
        self.placement_strategies: list[PlacementStrategy] = []

        self._create_placements()

    def _create_placements(self):
        self.placement_strategies.append(
            GridByHeightPlacement(press_sheet=self.press_sheet, list_size=self.list_size)
        )
        self.placement_strategies.append(
            GridByWidthPlacement(press_sheet=self.press_sheet, list_size=self.list_size)
        )

    def get_placements(self) -> list[PlacementStrategy]:
        return self.placement_strategies
