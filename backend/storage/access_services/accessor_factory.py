from backend.models.order import Order
from backend.storage.access_services.crud_accessor import CRUDAccessor
from backend.storage.mappers.base_mapper import BaseMapper
from backend.storage.repositories.base import BaseRepository
from backend.storage.tables import OrderEntity


class AccessorFactory:
    @classmethod
    def get_order_crud_accessor(cls) -> CRUDAccessor:
        return CRUDAccessor(
            BaseRepository(OrderEntity),
            BaseMapper(Order, OrderEntity),
        )
