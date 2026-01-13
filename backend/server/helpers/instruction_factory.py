import math

from backend.cost_reporter.calculators.exeptions.item_size_exception import ItemSizeException
from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_optimizer import \
    PlacementOptimizer
from backend.instruction_maker.instruction_model import InstructionModel
from backend.models import Printing


class InstructionService:
    """Построение модели инструкции для производства."""

    def build_instruction_model(self, order_id: int, unit_count: int, printing: Printing) -> InstructionModel:
        optimizer = PlacementOptimizer(
            press_sheet=printing.production.press_sheet,
            list_size=printing.edition.list_size
        )
        solution = optimizer.get_best_solution()
        product_per_sheet = solution.get_items_count()

        if product_per_sheet == 0:
            raise ItemSizeException()

        sheet_count = math.ceil(printing.edition.count / product_per_sheet)

        return InstructionModel(
            order_id=order_id,
            unit_count=unit_count,
            comment=printing.comment,
            density=printing.edition.density,
            press_sheet=printing.production.press_sheet,
            chroma=printing.edition.chroma,
            lamination=printing.edition.lamination,
            die_cutting=printing.edition.die_cutting,
            sheet_count=sheet_count,
            fitting_count=printing.production.sheet_by_fitting,
            edition_count=printing.edition.count,
            list_size=printing.edition.list_size,
            product_per_sheet=product_per_sheet
        )
