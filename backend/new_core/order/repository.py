"""Order persistence contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.order.order import Order, OrderID

OrderStoreOperation = Literal["take"]


class OrderNotFound(Exception):
    """Reports that there is no order with this id."""

    def __init__(
        self,
        operation: OrderStoreOperation,
        order_id: OrderID,
    ) -> None:
        """Builds the repository error text.

        :param operation:
        :param order_id:

        :return: sets the message
        ``{operation}: заказа нет, id={order_id.value}``.
        """
        super().__init__(f"{operation}: заказа нет, id={order_id.value}")


class OrderRepository(Protocol):
    """Loads customer orders by id."""

    def take(self, order_id: OrderID) -> Order:
        """Returns the order with this id.

        :param order_id:

        :raises OrderNotFound: if there is no order.

        :return: the order row.
        """
        ...
