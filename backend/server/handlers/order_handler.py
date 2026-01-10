from starlette.responses import StreamingResponse

from backend.models import Status, Order, PrintingCostReport, OrderCostReport
from backend.server.handlers.entity_handler import EntityHandler
from backend.server.handlers.instruction_handler import InstructionHandler
from backend.server.helpers.instruction_factory import InstructionService
from backend.server.helpers.order_factory import OrderFactoryService
from backend.server.models.change_payload import ChangePayload
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

    async def delay(self, payload: Order):
        """Создать заказ со статусом 'отложено'."""
        order = self._order_factory.fit_order(payload, Status("Отложен"))
        await self._service.add_models([order])

    async def accept(self, payload: Order) -> StreamingResponse:
        """Создать заказ со статусом 'в работе' и вернуть PDF-инструкцию."""
        order = self._order_factory.fit_order(payload, Status("В работе"))
        order = (await self._service.add_models([order]))[0]

        # TODO из одного хендлера лезем в другой. создать отдельный класс?
        instruction = await InstructionHandler().take_instruction_on_order(order.id)

        return instruction

    async def change(self, payload: ChangePayload):
        """Изменить статус существующего заказа."""
        order = await self._service.get_model_by_id(payload.order_id)
        order.status = payload.new_status
        await self._service.update_models([order])

    def cost_report(self, order: Order) -> OrderCostReport:
        order = self._order_factory.fit_order(order, None)
        return order.cost_report

    async def get_all(self) -> list[MODEL]:
        orders = await super().get_all()
        for order in orders:
            for printing in order.printings:
                printing.edition.count /= order.unit_count
        return orders

    async def get(self, id: int) -> MODEL:
        order: Order = await super().get(id)
        for printing in order.printings:
            printing.edition.count /= order.unit_count
        return order


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
