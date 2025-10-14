from io import BytesIO

from starlette.responses import StreamingResponse

from backend.instruction_maker.instruction_builder_factory import InstructionBuilderFactory
from backend.models import Status
from backend.models.order import Order
from backend.server.handlers.entity_handler import EntityHandler
from backend.server.helpers.instruction_factory import InstructionService
from backend.server.helpers.order_factory import OrderFactoryService
from backend.server.models.change_payload import ChangePayload
from backend.server.models.order_payload import OrderPayload
from backend.storage.access_services.accessor_factory import AccessorFactory


class OrderHandler(EntityHandler):
    MODEL = Order

    def __init__(
        self,
        order_factory: OrderFactoryService | None = None,
        instruction_service: InstructionService | None = None,
    ):
        super().__init__(AccessorFactory.get_order_crud_accessor())
        self._order_factory = order_factory or OrderFactoryService()
        self._instruction_service = instruction_service or InstructionService()

    async def delay(self, payload: OrderPayload):
        """Создать заказ со статусом 'отложено'."""
        order = await self._order_factory.create_order(payload, Status(1))
        await self._service.add_models([order])

    async def accept(self, payload: OrderPayload) -> StreamingResponse:
        """Создать заказ со статусом 'в работе' и вернуть PDF-инструкцию."""
        order = await self._order_factory.create_order(payload, Status(2))
        order = (await self._service.add_models([order]))[0]

        instruction_model = self._instruction_service.build_instruction_model(order, payload)
        builder = InstructionBuilderFactory(instruction_model).make_instruction_builder()
        pdf_bytes = builder.build_pdf()

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=instruction.pdf"}
        )

    async def change(self, payload: ChangePayload):
        """Изменить статус существующего заказа."""
        order = await self._service.get_model_by_id(payload.order_id)
        order.status = payload.new_status
        await self._service.update_models([order])

    async def get_all(self) -> list[MODEL]:
        return await super().get_all()

    async def get(self, id: int) -> MODEL:
        return await super().get(id)

    async def create(self, data: MODEL) -> MODEL:
        return await super().create(data)

    async def create_bulk(self, data: list[MODEL]) -> list[MODEL]:
        return await super().create_bulk(data)

    async def update(self, id: int, data: MODEL) -> MODEL:
        return await super().update(id, data)

    async def update_bulk(self, data: list[MODEL]) -> list[MODEL]:
        return await super().update_bulk(data)

    async def delete(self, id: int) -> dict:
        return await super().delete(id)
