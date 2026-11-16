"""Behavior of listing stored orders."""

import pytest

from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.repository import OrderNotFound
from backend.new_core.order.product import Product
from backend.new_core.values.percent import Percent
from backend.new_core.application_services.order import OrderService
from backend.test.new_core.in_memory_repositories import (
    InMemoryOrderRepository,
    InMemoryUnitOfWork,
)
from backend.test.new_core.test_print_run import (
    _RunPricingFixtures,
    build_worked_run,
    order_service,
)
from backend.test.storage.helpers import TEST_ORDER_CREATED_AT


__all__ = [
    "test_should_list_orders_with_the_larger_id_first_when_a_limit_is_set",
    "test_should_return_an_empty_list_when_there_are_no_orders",
    "test_get_order_returns_the_stored_order",
    "test_get_order_raises_when_the_id_is_missing",
]

def _order(order_id: int) -> Order:
    """Handles order.

    :param order_id: id of the order.

    :return: the Order result.
    """
    run, _, _, _, _ = build_worked_run(
        with_print=False,
        with_laminate=False,
        with_cut=False,
    )
    return Order(
        id=OrderID(order_id),
        product=Product(
            parts_markup=Percent(0),
            blocks=(
                run.block,
            ),
            operations=()),
        count=1,
        description="",
        created_at=TEST_ORDER_CREATED_AT,
    )


def _list_service(orders: InMemoryOrderRepository) -> OrderService:
    """Handles list service.

    :param orders: the orders.

    :return: the OrderService result.
    """
    uow = InMemoryUnitOfWork(orders=orders)
    return order_service(uow, _RunPricingFixtures())


def test_should_list_orders_with_the_larger_id_first_when_a_limit_is_set():
    """Handles test should list orders with the larger id first when a limit is set.
    """
    orders = InMemoryOrderRepository(
        orders={
            _order(1).id: _order(1),
            _order(5).id: _order(5),
            _order(3).id: _order(3),
        },
    )
    listed = _list_service(orders).get_orders(2)
    assert [item.id.value for item in listed] == [5, 3]


def test_should_return_an_empty_list_when_there_are_no_orders():
    """Handles test should return an empty list when there are no orders.
    """
    listed = _list_service(InMemoryOrderRepository()).get_orders(10)
    assert listed == ()


def test_get_order_returns_the_stored_order():
    """Handles test get order returns the stored order.
    """
    stored = _order(4)
    orders = InMemoryOrderRepository(orders={stored.id: stored})

    assert _list_service(orders).get_order(stored.id) is stored


def test_get_order_raises_when_the_id_is_missing():
    """Handles test get order raises when the id is missing.
    """
    with pytest.raises(OrderNotFound):
        _list_service(InMemoryOrderRepository()).get_order(OrderID(404))
