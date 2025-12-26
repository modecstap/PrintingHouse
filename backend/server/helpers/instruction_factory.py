import math

from backend.cost_reporter.calculators.exeptions.item_size_exception import ItemSizeException
from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_optimizer import \
    PlacementOptimizer
from backend.instruction_maker.instruction_model import InstructionModel
from backend.server.models.order_payload import OrderPayload


class InstructionService:
    """Построение модели инструкции для производства."""

    def build_instruction_model(self, order_id: int, payload: OrderPayload) -> InstructionModel:
        optimizer = PlacementOptimizer(
            press_sheet=payload.production.press_sheet,
            list_size=payload.edition.list_size
        )
        solution = optimizer.get_best_solution()
        product_per_sheet = solution.get_items_count()

        if product_per_sheet == 0:
            raise ItemSizeException()

        sheet_count = math.ceil(payload.edition.count / product_per_sheet)

        return InstructionModel(
            order_id=order_id,
            comment=payload.comment,
            density=payload.edition.density,
            press_sheet=payload.production.press_sheet,
            chroma=payload.edition.chroma,
            lamination=payload.edition.lamination,
            die_cutting=payload.edition.die_cutting,
            sheet_count=sheet_count,
            fitting_count=payload.production.sheet_by_fitting,
            edition_count=payload.edition.count,
            list_size=payload.edition.list_size,
            product_per_sheet=product_per_sheet
        )
