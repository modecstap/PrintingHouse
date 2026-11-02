from typing import Literal, Protocol

from backend.core.order import Order
from backend.core.reports import CostReport

OrderId = int

StoreOperation = Literal[
    "save",
    "take",
    "attach",
    "reports",
    "delete",
    "take_all",
    "save_with_report",
    "reference",
    "set_reference",
]


class OrderNotFound(Exception):
    def __init__(
        self,
        operation: StoreOperation,
        order_id: OrderId,
    ) -> None:
        """Reports that there is no order with this id.

        :param operation:
        :param order_id:

        :return: the text "{operation}: заказа нет, id={order_id}".
        """
        super().__init__(f"{operation}: заказа нет, id={order_id}")


class OrderStoreUnavailable(Exception):
    def __init__(
        self,
        operation: StoreOperation,
        order_id: OrderId | None,
    ) -> None:
        """Reports that there is no connection to the database.

        :param operation:
        :param order_id: may be None if the break happened while inserting a new order.

        :return: the text "{operation}: нет соединения с базой, id={order_id}".
        The text has no driver message, database address, or password.
        """
        super().__init__(
            f"{operation}: нет соединения с базой, id={order_id}"
        )


class WorkplaceOrderRepository(Protocol):
    def save(self, order: Order) -> OrderId:
        """Saves the order's calculation data, comment, and status.

        :param order:

        :raises OrderNotFound: if the given id has no row.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the id of the saved order. When the id is empty,
        the database assigns it, and it is known only from the return.
        When the id already exists, that same id is returned.
        """
        ...

    def take(self, order_id: OrderId) -> Order:
        """Returns the whole order with this id, without the CostReport list.

        :param order_id:

        :raises OrderNotFound: if there is no row.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the order with calculation data, comment, status,
        and the insertion date.
        """
        ...

    def attach(self, report: CostReport, order_id: OrderId) -> None:
        """Appends one report to the end of the order's report list.

        :param report:
        :param order_id:

        :raises OrderNotFound: if the order does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        ...

    def reports(self, order_id: OrderId) -> list[CostReport]:
        """Returns the order's attached reports.

        :param order_id:

        :raises OrderNotFound: if the order does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: an empty list if attach has not happened yet.
        Otherwise the reports are in the order of successful attach calls,
        from the earliest.
        """
        ...

    def take_all(self) -> list[Order]:
        """Returns every order row, without CostReport.

        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: each row once, by descending id. No rows: an empty list.
        """
        ...

    def delete(self, order_id: OrderId) -> None:
        """Deletes this order.

        :param order_id:

        :raises OrderNotFound: if the order does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        ...

    def save_with_report(
        self, order: Order, report: CostReport
    ) -> OrderId:
        """Saves the order and appends the report in one transaction.

        :param order:
        :param report:

        :raises OrderNotFound: if the given id has no row. The text is built by save.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the id of the saved order. An empty id is assigned by the database.
        An existing id is returned unchanged.
        """
        ...

    def reference(self) -> Order | None:
        """Returns the reference if the row exists.

        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: an order with id None and no creation_date. No row: None.
        """
        ...

    def set_reference(self, order: Order) -> None:
        """Replaces the single reference record.

        :param order:

        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        ...
