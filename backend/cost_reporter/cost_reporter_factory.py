from backend.cost_reporter.calculators.edition_calculator import EditionCalculator
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

        placement = self._create_placement()
        sheet_calculator = self._create_sheet_calculator(placement)
        edition_calculator = self._create_edition_calculator(sheet_calculator)
        tax_calculator = self._create_tax_calculator(edition_calculator)

        self._sheet_calculator = sheet_calculator
        self._edition_calculator = edition_calculator
        self._tax_calculator = tax_calculator

    # --- Вспомогательные шаги сборки ---

    def _create_placement(self):
        """Оптимизатор размещения на печатном листе."""
        return PlacementOptimizer(
            press_sheet=self._production.press_sheet,
            list_size=self._edition.list_size,
        ).get_best_solution()

    def _create_sheet_calculator(self, placement):
        """Конструирование калькулятора стоимости листа."""
        builder = SheetCostBuilder(
            edition=self._edition,
            production=self._production,
            placement=placement,
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

        # Дополнительные опции
        if self._edition.die_cutting:
            builder = builder.with_die_cutting()

        builder = (
            builder
            .with_volume_markup()
            .with_tax_compensation()
        )

        return SheetCalculator(
            items_count=self._edition.count,
            placement=placement,
            cost_calculator=builder.get_calculator(),  # исправлено название
        )

    def _create_edition_calculator(self, sheet_calculator: SheetCalculator):
        """Калькулятор тиража."""
        return EditionCalculator(
            item_count=self._edition.count,
            item_per_sheet=sheet_calculator.items_per_sheet(),
            unit_cost=sheet_calculator.get_unit_cost(),
            unit_cost_price=sheet_calculator.get_unit_cost_price(),
            markup=self._edition.markup
        )

    def _create_tax_calculator(self, edition_calculator: EditionCalculator):
        """Калькулятор налогов."""
        return TaxCalculator(tax_rate=self._production.tax_rate, profit_before_tax=edition_calculator.profit())

    # --- Публичный интерфейс ---

    def create_reporter(self) -> CostReporter:
        """Создаёт готовый объект для генерации отчёта по стоимости."""
        return CostReporter(
            sheet_calculator=self._sheet_calculator,
            edition_calculator=self._edition_calculator,
            tax_calculator=self._tax_calculator,
        )
