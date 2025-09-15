from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_strategies.pacement_strategy import \
    PlacementStrategy


class GridByHeightPlacement(PlacementStrategy):
    """
    Размещение изделий в сетку с приоритетом по высоте.
    """

    def _calculate_counts(self):
        self.count_x = self.usable_width // self.item_height
        self.count_y = self.usable_height // self.item_width
