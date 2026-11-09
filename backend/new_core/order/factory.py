"""Builds orders with ids from the store."""

from backend.new_core.order.order import Order
from backend.new_core.order.product import Product
from backend.new_core.order.repository import OrderRepository


class OrderFactory:
    """Allocates order ids and builds orders."""

    def __init__(self, orders: OrderRepository) -> None:
        self._orders = orders

    def create(self, product: Product, count: int) -> Order:
        """Builds an order with a generated id.

        :param product:
        :param count:

        :return: the new order.
        """
        return Order(
            id=self._orders.generate_id(),
            product=product,
            count=count,
        )
