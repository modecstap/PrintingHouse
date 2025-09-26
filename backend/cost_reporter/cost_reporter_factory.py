from backend.cost_reporter.calculators.edition_calculator import EditionCalculator
from backend.cost_reporter.calculators.item_calculator import ItemCalculator
from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_optimizer import \
    PlacementOptimizer
from backend.cost_reporter.calculators.sheet_calculator.sheet_calculator import SheetCalculator
from backend.cost_reporter.calculators.sheet_calculator.sheet_cost_builder import SheetCostBuilder
from backend.cost_reporter.calculators.tax_calculator import TaxCalculator
from backend.cost_reporter.cost_reporter import CostReporter
from backend.cost_reporter.models.edition import Edition
from backend.cost_reporter.models.production import Production


class CostReporterFactory:
    """
    Фабрика для сборки готового CostReporter.
    Отвечает за создание и связывание зависимостей.
    """

    def __init__(self, edition_data: Edition, production_data: Production):
        self._edition = edition_data
        self._production = production_data

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
            placement=self._placement,
        )

        # Базовые шаги
        builder = (
            builder
            .with_paper()
            .with_ink()
            .with_printer_salary()
            .with_lamination()
            .with_cut()
            .with_markup()
        )

        if self._edition.die_cutting:
            builder = builder.with_die_cutting()

        builder = (
            builder
            .with_volume_markup()
            .with_tax_compensation()
        )

        return SheetCalculator(
            items_count=self._edition.count,
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
            markup=self._edition.markup
        )

    def _create_tax_calculator(self):
        """Калькулятор налогов."""
        return TaxCalculator(
            tax_rate=self._production.tax_rate,
            profit_before_tax=self._edition_calculator.profit()
        )

    def _create_item_calculator(self) -> ItemCalculator:
        return ItemCalculator(
            sheet_cost=self._sheet_calculator.get_cost(),
            sheet_cost_price=self._sheet_calculator.get_cost_price(),
            sheet_by_fitting=self._production.sheet_by_fitting,
            item_per_sheet=self._placement.get_items_count(),
            item_count=self._edition.count
        )

    def create_reporter(self) -> CostReporter:
        """Создаёт готовый объект для генерации отчёта по стоимости."""
        return CostReporter(
            sheet_calculator=self._sheet_calculator,
            edition_calculator=self._edition_calculator,
            item_calculator=self._item_calculator,
            tax_calculator=self._tax_calculator,
        )
