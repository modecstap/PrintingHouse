"""Use cases that quote, save, list, and price orders."""

from __future__ import annotations

from backend.new_core.accountant.accountant import Accountant
from backend.new_core.accountant.order_report import OrderReport
from backend.new_core.accountant.pricing.factory import PricingStrategyFactory
from backend.new_core.accountant.run_estimate import RunEstimate
from backend.new_core.order.factory import OrderFactory
from backend.new_core.order.order import Order, OrderContent, OrderID
from backend.new_core.order.product import Product
from backend.new_core.order.repository import OrderIdOccupied
from backend.new_core.application_services.unit_of_work import OrderUnitOfWork
from backend.new_core.print_run.factory import PrintRunFactory
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.values.percent import Percent

__all__ = [
    "OrderIdAllocationFailed",
    "OrderService",
]

_MAX_ORDER_ID_ATTEMPTS = 3


class OrderIdAllocationFailed(Exception):
    """Reports that save exhausted occupied-id retries."""

    def __init__(self, last_occupied: OrderID) -> None:
        """Initializes this instance.

        :param last_occupied: the last occupied.
        """
        super().__init__(
            f"save: не удалось выделить id заказа за {_MAX_ORDER_ID_ATTEMPTS} "
            f"попытки, id={last_occupied.value}",
        )
        self.last_occupied = last_occupied


class OrderService:
    """Quotes, saves, lists, and builds price reports for orders."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        uow: OrderUnitOfWork,
        order_factory: OrderFactory,
        print_run_factory: PrintRunFactory,
        pricing_factory: PricingStrategyFactory,
    ) -> None:
        """:param uow:

        :param order_factory: the order factory.
        :param print_run_factory: the print run factory.
        :param pricing_factory: the pricing factory.
        :param uow: the uow.
        """
        self._uow = uow
        self._order_factory = order_factory
        self._print_run_factory = print_run_factory
        self._pricing_factory = pricing_factory

    def get_orders(self, limit: int) -> tuple[Order, ...]:
        """Returns the latest orders by id.

        :param limit: the limit.

        :return: the tuple[Order, ...] result.
        """
        return self._uow.orders.take_latest(limit)

    def get_order(self, order_id: OrderID) -> Order:
        """Returns the order with this id.

        :param order_id: id of the order.

        :raises OrderNotFound: if the order does not exist.

        :return: the Order result.
        """
        return self._uow.orders.take(order_id)

    def order_report(self, order_id: OrderID) -> OrderReport:
        """Prices the order after tax compensation.

        :param order_id: id of the order.

        :raises OrderNotFound: if the order does not exist.
        :raises KeyError: if a catalog id from a run operation is missing.

        :return: the OrderReport result.
        """
        order = self._uow.orders.take(order_id)
        parts_markup = order.product.parts_markup
        runs = self._uow.print_runs.take_all_for_order(order_id)
        estimates = tuple(
            self._run_estimate(run, parts_markup)
            for run in runs
        )
        return Accountant().order_report(order, estimates)

    def quote(self, product: Product, count: int) -> OrderReport:
        """Prices the product without persisting an order.

        :param product: the product.
        :param count: the count.

        :raises KeyError: if a catalog id is missing.
        :raises TypeError: if an operation type is not supported.
        :raises InvalidInput: if the product or run data is invalid.

        :return: the OrderReport result.
        """
        order = self._order_factory.create(product, count)
        runs = self._made_run_for_order(order)
        parts_markup = order.product.parts_markup
        estimates = tuple(
            self._run_estimate(run, parts_markup) for run in runs
        )
        return Accountant().order_report(order, estimates)

    def save(self, product: Product, count: int,
             description: str = "") -> OrderID:
        """Persists the order and one print run per block.

        :param product: the product.
        :param count: the count.
        :param description: the description.

        :raises OrderIdAllocationFailed: after three occupied order ids.
        :raises InvalidInput: if the product or run data is invalid.
        :raises RuntimeError: when the operation fails.

        :return: the OrderID result.
        """
        last_occupied: OrderIdOccupied | None = None
        for _ in range(_MAX_ORDER_ID_ATTEMPTS):
            try:
                def work() -> OrderID:
                    """Handles work.

                    :return: the OrderID result.
                    """
                    order = self._order_factory.create(product, count,
                                                       description)
                    runs = self._made_run_for_order(order)
                    self._uow.orders.save(order)
                    self._uow.print_runs.save_all_for_order(order.id, runs)
                    return order.id

                return self._uow.transaction(work)
            except OrderIdOccupied as exc:
                last_occupied = exc
        if last_occupied is None:
            raise RuntimeError("save exhausted retries without OrderIdOccupied")
        raise OrderIdAllocationFailed(last_occupied.order_id) from last_occupied

    def replace(
        self,
        order_id: OrderID,
        content: OrderContent,
    ) -> OrderID:
        """Replaces an existing order and its print runs.

        :param order_id: id of the order.
        :param content: the content.

        :raises OrderNotFound: if the order does not exist.
        :raises KeyError: if a catalog id is missing.
        :raises TypeError: if an operation type is not supported.
        :raises InvalidInput: if the product or run data is invalid.

        :return: the OrderID result.
        """

        def work() -> OrderID:
            """Handles work.

            :return: the OrderID result.
            """
            existing = self._uow.orders.take(order_id)
            order = Order(
                id=order_id,
                product=content.product,
                count=content.count,
                description=content.description,
                created_at=existing.created_at,
            )
            runs = self._made_run_for_order(order)
            self._uow.orders.replace(order)
            self._uow.print_runs.save_all_for_order(order_id, runs)
            return order_id

        return self._uow.transaction(work)

    def _run_estimate(
            self,
            run: PrintRun,
            parts_markup: Percent) -> RunEstimate:
        """Turns run operations into one run estimate.

        :param run: the run.
        :param parts_markup: the parts markup.

        :raises KeyError: if a catalog id from an operation is missing.
        :raises TypeError: if an operation type is not supported.

        :return: the RunEstimate result.
        """
        strategies = [
            self._pricing_factory.create(operation, run)
            for operation in run.block.operations
        ]
        return RunEstimate.create(
            strategies, run=run, parts_markup=parts_markup)

    def _made_run_for_order(
        self,
        order: Order,
    ) -> tuple[PrintRun, ...]:
        """Handles made run for order.

        :param order: the order.

        :return: the tuple[PrintRun, ...] result.
        """
        runs = tuple(
            self._print_run_factory.create(
                for_order=order.id,
                block=block,
                required_count=order.count * block.count,
            )
            for block in order.product.blocks
        )
        return runs
