from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_strategies.pacement_strategy import \
    PlacementStrategy


class GridByWidthPlacement(PlacementStrategy):
    """
    Размещение изделий в сетку с приоритетом по ширине.
    """

    def _calculate_counts(self):
        self.count_x = self.usable_width // self.item_width
        self.count_y = self.usable_height // self.item_height
