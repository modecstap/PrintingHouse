from cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_strategies.pacement_strategy import \
    PlacementStrategy
from cost_reporter.calculators.sheet_calculator.stages.cut_stage import CutStage
from cost_reporter.calculators.sheet_calculator.stages.die_cutting_stage import DieCuttingStage
from cost_reporter.calculators.sheet_calculator.stages.empty_stage import EmptyStage
from cost_reporter.calculators.sheet_calculator.stages.i_stage import IStage
from cost_reporter.calculators.sheet_calculator.stages.ink_stage import InkStage
from cost_reporter.calculators.sheet_calculator.stages.lamination_stage import LaminationStage
from cost_reporter.calculators.sheet_calculator.stages.paper_stage import PaperStage
from cost_reporter.models.edition import Edition
from cost_reporter.models.production import Production


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

    def with_ink(self):
        self._calculator = InkStage(
            previous_stage=self._calculator,
            black_ink_cost=self._production.black_ink_cost,
            color_ink_cost=self._production.ink_cost,
            chroma=self._edition.chroma
        )
        return self

    def with_lamination(self):
        self._calculator = LaminationStage(
            previous_stage=self._calculator,
            lamination=self._edition.lamination
        )
        return self

    def with_die_cutting(self):
        self._calculator = DieCuttingStage(
            previous_stage=self._calculator,
            die_cutting_cost=self._production.die_cutting_cost,
        )
        return self

    def with_cut(self):
        self._calculator = CutStage(
            previous_stage=self._calculator,
            cut_cost=self._production.cutting_cost,
            placement=self._placement
        )
        return self
