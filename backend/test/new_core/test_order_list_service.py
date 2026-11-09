"""Behavior of listing stored orders."""

from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.product import Product
from backend.new_core.order.service import OrderService
from backend.test.new_core.in_memory_repositories import (
    InMemoryCutterOperatorRepository,
    InMemoryDieCutterOperatorRepository,
    InMemoryLaminatorOperatorRepository,
    InMemoryLaminatorRepository,
    InMemoryOrderRepository,
    InMemoryPressOperatorRepository,
    InMemoryPrinterRepository,
    InMemoryUnitOfWork,
)
from backend.test.new_core.test_print_run import build_worked_run


def _order(order_id: int) -> Order:
    run, *_ = build_worked_run(
        with_print=False,
        with_laminate=False,
        with_cut=False,
    )
    return Order(
        id=OrderID(order_id),
        product=Product(blocks=(run.block,), operations=()),
        count=1,
    )


def _list_service(orders: InMemoryOrderRepository) -> OrderService:
    return OrderService(
        uow=InMemoryUnitOfWork(orders=orders),
        printers=InMemoryPrinterRepository(),
        press_operators=InMemoryPressOperatorRepository(),
        laminators=InMemoryLaminatorRepository(),
        laminator_operators=InMemoryLaminatorOperatorRepository(),
        cutter_operators=InMemoryCutterOperatorRepository(),
        die_cut_operators=InMemoryDieCutterOperatorRepository(),
    )


def test_should_list_orders_with_the_larger_id_first_when_a_limit_is_set():
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
    listed = _list_service(InMemoryOrderRepository()).get_orders(10)
    assert listed == ()
