import math
from io import BytesIO

from starlette.responses import StreamingResponse

from backend.cost_reporter.calculators.exeptions.item_size_exception import ItemSizeException
from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_optimizer import \
    PlacementOptimizer
from backend.instruction_maker.instruction_builder_factory import InstructionBuilderFactory
from backend.instruction_maker.instruction_model import InstructionModel
from backend.server.helpers.instruction_factory import InstructionService
from backend.server.models.instruction_payload import InstructionPayload
from backend.server.models.order_payload import OrderPayload
from backend.storage.access_services.accessor_factory import AccessorFactory


class InstructionHandler:

    def take_instruction(self, payload: InstructionPayload) -> StreamingResponse:
        instruction_model = InstructionService().build_instruction_model(payload.order_id, payload)
        builder = InstructionBuilderFactory(instruction_model).make_instruction_builder()
        pdf_bytes = builder.build_pdf()
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=instruction.pdf"}
        )

    async def take_instruction_on_order(self, order_id: int):
        order_repository = AccessorFactory.get_order_crud_accessor()
        order = await order_repository.get_model_by_id(order_id)

        instruction_model = InstructionService().build_instruction_model(
            order_id,
            OrderPayload(
                comment="",
                edition=order.edition,
                production=order.production
            )
        )
        builder = InstructionBuilderFactory(instruction_model).make_instruction_builder()
        pdf_bytes = builder.build_pdf()
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=instruction.pdf"}
        )

