from item_placement_calculator.placement_strategies.pacement_strategy import PlacementStrategy
from item_placement_calculator.placement_strategies.placement_factory import PlacementFactory
from models.list_size import ListSize
from models.press_sheet import PressSheet


class PlacementOptimizer:
    """
    Находит решение при котором на печатном листе располагается максимальное количество изделий
    """

    def __init__(self, press_sheet: PressSheet, list_size: ListSize):
        self._placements = PlacementFactory(
            press_sheet=press_sheet,
            list_size=list_size
        ).get_placements()

        self._best_solution = self._placements[0]

        self._find_best_solution()

    def _find_best_solution(self):
        for placement in self._placements:
            item_count = placement.get_items_count()
            if self._best_solution.get_items_count() > item_count:
                self._best_solution = placement

    def get_items_per_sheet(self) -> int:
        return self._best_solution.get_items_count()

    def get_cut_count(self) -> int:
        return self._best_solution.get_cut_count()
