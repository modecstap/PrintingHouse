from calculators.item_placement_calculator.placement_strategies.pacement_strategy import PlacementStrategy
from models.edition import Edition
from models.production import Production
from stages.cut_stage import CutStage
from stages.die_cutting_stage import DieCuttingStage
from stages.empty_stage import EmptyStage
from stages.i_stage import IStage
from stages.ink_stage import InkStage
from stages.lamination_stage import LaminationStage
from stages.paper_stage import PaperStage


class ProductionBuilder:
    def __init__(
            self,
            edition: Edition,
            production: Production,
            placement: PlacementStrategy
    ):
        self._edition = edition
        self._production = production
        self._placement = placement
        self._production_line = EmptyStage()

    def get_production_line(self) -> IStage:
        return self._production_line

    def with_paper(self):
        self._production_line = PaperStage(
            previous_stage=self._production_line,
            press_sheet=self._production.press_sheet,
            kilograms_paper_cost=self._production.paper_cost,
            density=self._edition.density
        )

    def with_ink(self):
        self._production_line = InkStage(
            previous_stage=self._production_line,
            black_ink_cost=self._production.black_ink_cost,
            color_ink_cost=self._production.ink_cost,
            chroma=self._edition.chroma
        )

    def with_lamination(self):
        self._production_line = LaminationStage(
            previous_stage=self._production_line,
            lamination=self._edition.lamination
        )

    def with_die_cutting(self):
        self._production_line = DieCuttingStage(
            previous_stage=self._production_line,
            die_cutting_cost=self._production.die_cutting_cost,
            die_cutting=self._edition.die_cutting
        )

    def with_cut(self):
        self._production_line = CutStage(
            previous_stage=self._production_line,
            cut_cost=self._production.cutting_cost,
            placement=self._placement
        )
