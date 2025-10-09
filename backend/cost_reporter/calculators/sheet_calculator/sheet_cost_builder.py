import math

from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_strategies.pacement_strategy import \
    PlacementStrategy
from backend.cost_reporter.calculators.sheet_calculator.stages.cut_stage import CutStage
from backend.cost_reporter.calculators.sheet_calculator.stages.die_cutting_stage import DieCuttingStage
from backend.cost_reporter.calculators.sheet_calculator.stages.empty_stage import EmptyStage
from backend.cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage
from backend.cost_reporter.calculators.sheet_calculator.stages.lamination_stage import LaminationStage
from backend.cost_reporter.calculators.sheet_calculator.stages.markup_stage import MarkupStage
from backend.cost_reporter.calculators.sheet_calculator.stages.paper_stage import PaperStage
from backend.cost_reporter.calculators.sheet_calculator.stages.print_stage import PrintStage
from backend.cost_reporter.calculators.sheet_calculator.stages.tax_compensation_stage import TaxCompensationStage
from backend.cost_reporter.calculators.sheet_calculator.stages.volume_markup_stage import VolumeMarkupStage
from backend.models import Edition
from backend.models import Production


class SheetCostBuilder:
    """
    Строит цепочки расчёта стоимости печатного листа.
    Позволяет пошагово добавлять стадии (бумага, краска, ламинация и т.д.)
    и получить итоговый калькулятор через.
    """

    def __init__(
            self,
            edition: Edition,
            production: Production,
            placement: PlacementStrategy
    ):
        self._edition = edition
        self._production = production
        self._placement = placement
        self._calculator = EmptyStage()
        self._sheet_count = math.ceil(
            self._edition.count /
            self._placement.get_items_count()
        )

    def get_calculator(self) -> IStage:
        return self._calculator

    def with_paper(self):
        self._calculator = PaperStage(
            previous_stage=self._calculator,
            press_sheet=self._production.press_sheet,
            kilograms_paper_cost=self._production.paper_cost,
            density=self._edition.density
        )
        return self

    def with_print(self):
        self._calculator = PrintStage(
            previous_stage=self._calculator,
            salary_by_sheet=self._production.printer_salary,
            black_ink_cost=self._production.black_ink_cost,
            color_ink_cost=self._production.ink_cost,
            chroma=self._edition.chroma
        )
        return self

    def with_lamination(self):
        self._calculator = LaminationStage(
            previous_stage=self._calculator,
            lamination=self._edition.lamination,
            sheet_lamination_cost=self._production.lamination_cost
        )
        return self

    def with_die_cutting(self):
        self._calculator = DieCuttingStage(
            previous_stage=self._calculator,
            die_cutting_cost=self._production.die_cutting_cost,
        )
        return self

    def with_cut(self):
        # TODO вынести расчёт количества листов в стопке
        sheet_in_stack = max(
            math.ceil(
                self._production.cutter.stack_height *
                1200 /
                self._edition.density
            ),
            0
        )
        self._calculator = CutStage(
            previous_stage=self._calculator,
            cut_cost=self._production.cutting_cost,
            cut_count=self._placement.get_cut_count(),
            sheet_count=self._sheet_count,
            sheet_in_stack=sheet_in_stack
        )
        return self

    def with_markup(self):
        self._calculator = MarkupStage(
            previous_stage=self._calculator,
            markup=self._production.markup
        )
        return self

    def with_tax_compensation(self):
        self._calculator = TaxCompensationStage(
            previous_stage=self._calculator,
            tax_rate=self._production.tax_rate
        )
        return self

    def with_volume_markup(self):
        self._calculator = VolumeMarkupStage(
            previous_stage=self._calculator,
            sheet_count=self._sheet_count
        )
        return self
