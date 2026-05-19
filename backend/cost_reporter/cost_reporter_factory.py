from backend.cost_reporter.calculators.edition_calculator import EditionCalculator
from backend.cost_reporter.calculators.item_calculator import ItemCalculator
from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_optimizer import \
    PlacementOptimizer
from backend.cost_reporter.calculators.sheet_calculator.sheet_calculator import SheetCalculator
from backend.cost_reporter.calculators.sheet_calculator.sheet_cost_builder import SheetCostBuilder
from backend.cost_reporter.calculators.tax_calculator import TaxCalculator
from backend.cost_reporter.printing_cost_reporter import PrintingCostReporter
from backend.models import Edition, Economy, Lamination
from backend.models import Production


class CostReporterFactory:
    """
    Фабрика для сборки готового PrintingCostReporter.
    Отвечает за создание и связывание зависимостей.
    """

    def __init__(self, edition: Edition, production: Production, economy: Economy):
        self._edition = edition
        self._production = production
        self._economy = economy

        self._placement = self._create_placement()

        self._sheet_calculator = self._create_sheet_calculator()
        self._item_calculator = self._create_item_calculator()
        self._edition_calculator = self._create_edition_calculator()
        self._tax_calculator = self._create_tax_calculator()

    # --- Вспомогательные шаги сборки ---

    def _create_placement(self):
        """Оптимизатор размещения на печатном листе."""
        return PlacementOptimizer(
            press_sheet=self._production.press_sheet,
            list_size=self._edition.list_size,
        ).get_best_solution()

    def _create_sheet_calculator(self) -> SheetCalculator:
        """Конструирование калькулятора стоимости листа."""
        builder = SheetCostBuilder(
            edition=self._edition,
            production=self._production,
            economy=self._economy,
            placement=self._placement,
        )

        # Базовые шаги
        builder = (
            builder
            .with_paper()
            .with_print()
            .with_cut()
        )

        if self._edition.lamination != Lamination.DONT:
            builder = builder.with_lamination()

        if self._edition.die_cutting:
            builder = builder.with_die_cutting()

        builder = (
            builder
            .with_markup()
            .with_volume_markup()
            .with_tax_compensation()
        )

        return SheetCalculator(
            placement=self._placement,
            cost_calculator=builder.get_calculator(),
        )

    def _create_edition_calculator(self):
        """Калькулятор тиража."""
        return EditionCalculator(
            item_count=self._edition.count,
            item_cost=self._item_calculator.get_item_cost(),
            item_cost_price=self._item_calculator.get_item_cost_price(),
            item_per_sheet=self._sheet_calculator.items_per_sheet(),
        )

    def _create_tax_calculator(self):
        """Калькулятор налогов."""
        return TaxCalculator(
            tax_rate=self._economy.tax_rate,
            profit_before_tax=self._edition_calculator.profit()
        )

    def _create_item_calculator(self) -> ItemCalculator:
        return ItemCalculator(
            sheet_cost=self._sheet_calculator.get_cost(),
            sheet_cost_price=self._sheet_calculator.get_cost_price(),
            item_per_sheet=self._placement.get_items_count(),
            item_count=self._edition.count
        )

    def create_reporter(self) -> PrintingCostReporter:
        """Создаёт готовый объект для генерации отчёта по стоимости."""
        return PrintingCostReporter(
            sheet_calculator=self._sheet_calculator,
            edition_calculator=self._edition_calculator,
            item_calculator=self._item_calculator,
            tax_calculator=self._tax_calculator,
        )
