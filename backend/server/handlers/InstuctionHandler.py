import math
from io import BytesIO

from starlette.responses import StreamingResponse

from backend.cost_reporter.calculators.exeptions.item_size_exception import ItemSizeException
from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_optimizer import \
    PlacementOptimizer
from backend.instruction_maker.instruction_builder_factory import InstructionBuilderFactory
from backend.instruction_maker.instruction_model import InstructionModel
from backend.server.models.instruction_payload import InstructionPayload


class InstructionHandler:

    def take_instruction(self, instruction_payload: InstructionPayload) -> StreamingResponse:
        product_per_sheet = PlacementOptimizer(
            press_sheet=instruction_payload.press_sheet,
            list_size=instruction_payload.list_size
        ).get_best_solution().get_items_count()

        try:
            sheet_count = instruction_payload.edition_count / product_per_sheet
        except ZeroDivisionError:
            raise ItemSizeException()
        sheet_count = math.ceil(sheet_count)

        instruction_model = InstructionModel(
            order_id=instruction_payload.order_id,
            density=instruction_payload.density,
            press_sheet=instruction_payload.press_sheet,
            chroma=instruction_payload.chroma,
            lamination=instruction_payload.lamination,
            die_cutting=instruction_payload.die_cutting,
            sheet_count=sheet_count,
            fitting_count=instruction_payload.fitting_count,
            edition_count=instruction_payload.edition_count,
            list_size=instruction_payload.list_size,
            product_per_sheet=product_per_sheet
        )
        factory = InstructionBuilderFactory(instruction_model=instruction_model)

        builder = factory.make_instruction_builder()
        pdf_bytes = builder.build_pdf()
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=instruction.pdf"}
        )
