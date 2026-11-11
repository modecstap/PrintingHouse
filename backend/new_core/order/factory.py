"""Builds orders with ids from the store."""

from datetime import UTC, datetime

from backend.new_core.order.order import Order
from backend.new_core.order.product import Product
from backend.new_core.order.repository import OrderRepository


class OrderFactory:
    """Allocates order ids and builds orders."""

    def __init__(self, orders: OrderRepository) -> None:
        self._orders = orders

    def create(self, product: Product, count: int, description: str = "") -> Order:
        """Builds an order with a generated id.

        :param product:
        :param count:
        :param description:

        :return: the new order.
        """
        return Order(
            id=self._orders.generate_id(),
            product=product,
            count=count,
            description=description,
            created_at=datetime.now(UTC),
        )
