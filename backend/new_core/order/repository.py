"""Order persistence contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.order.order import Order, OrderID

OrderStoreOperation = Literal["take", "save"]


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


class OrderIdOccupied(Exception):
    """Reports that an order id is already stored."""

    def __init__(
        self,
        operation: OrderStoreOperation,
        order_id: OrderID,
    ) -> None:
        """Builds the repository error text.

        :param operation:
        :param order_id:

        :return: sets the message
        ``{operation}: заказ уже есть, id={order_id.value}``.
        """
        self.order_id = order_id
        super().__init__(f"{operation}: заказ уже есть, id={order_id.value}")


class OrderRepository(Protocol):
    """Loads and stores customer orders by id."""

    def take(self, order_id: OrderID) -> Order:
        """Returns the order with this id.

        :param order_id:

        :raises OrderNotFound: if there is no order.

        :return: the order row.
        """
        ...

    def generate_id(self) -> OrderID:
        """Returns the next order id from the store sequence.

        :return: a new order id. It may already be occupied.
        """
        ...

    def save(self, order: Order) -> None:
        """Stores the order under its id.

        :param order:

        :raises OrderIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        ...

    def take_latest(self, limit: int) -> tuple[Order, ...]:
        """Returns stored orders with the largest ids first.

        :param limit: maximum row count. Zero: an empty tuple.

        :return: at most ``limit`` orders, by descending id.
        No rows: an empty tuple.
        """
        ...
