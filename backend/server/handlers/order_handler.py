from backend.models.order import Order
from backend.server.handlers.entity_handler import EntityHandler
from backend.storage.access_services.accessor_factory import AccessorFactory


class OrderHandler(EntityHandler):
    MODEL = Order

    def __init__(self):
        super().__init__(AccessorFactory.get_order_crud_accessor())

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
