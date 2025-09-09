from item_placement_calculator.placement_optimizer import PlacementOptimizer
from models.edition import Edition
from models.production import Production
from cost_reporter import CostReporter, SheetCalculator, CostCalculator, ProfitCalculator


class CostReporterFactory:
    """
    Фабрика для создания готового CostReporter.
    """

    def __init__(self, edition: Edition, production: Production):
        self._edition = edition
        self._production = production

    def build(self) -> CostReporter:
        sheet_calc = SheetCalculator(self._edition, self._production)
        cost_calc = CostCalculator()
        profit_calc = ProfitCalculator(self._edition, self._production)

        return CostReporter(sheet_calc, cost_calc, profit_calc)
