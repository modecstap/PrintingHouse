"""Behavior of reference catalog use cases."""

import pytest

from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.product import Product
from backend.new_core.order.repository import OrderNotFound
from backend.new_core.reference.reference import Reference
from backend.new_core.application_services.reference import ReferenceOrderService
from backend.test.new_core.in_memory_repositories import (
    InMemoryOrderRepository,
    InMemoryReferenceRepository,
)
from backend.test.new_core.test_print_run import build_worked_run
from backend.test.storage.helpers import TEST_ORDER_CREATED_AT


def _service(
    orders: InMemoryOrderRepository | None = None,
    references: InMemoryReferenceRepository | None = None,
) -> ReferenceOrderService:
    return ReferenceOrderService(
        references=references or InMemoryReferenceRepository(),
        orders=orders or InMemoryOrderRepository(),
    )


def test_references_returns_stored_rows_in_order():
    refs = InMemoryReferenceRepository()
    refs.save(Reference(name="a", description="one", order_id=OrderID(1)))
    refs.save(Reference(name="b", description="two", order_id=OrderID(2)))

    assert _service(references=refs).references() == tuple(refs.rows)


def test_save_stores_reference_when_order_exists():
    run, *_ = build_worked_run(with_print=False, with_laminate=False, with_cut=False)
    order = Order(
        id=OrderID(3),
        product=Product(blocks=(run.block,), operations=()),
        count=1,
        description="",
        created_at=TEST_ORDER_CREATED_AT,
    )
    orders = InMemoryOrderRepository(orders={order.id: order})
    refs = InMemoryReferenceRepository()
    service = _service(orders=orders, references=refs)
    row = Reference(name="ref", description="desc", order_id=order.id)

    service.save(row)

    assert refs.rows == [row]


def test_save_raises_when_order_is_missing():
    with pytest.raises(OrderNotFound):
        _service().save(
            Reference(name="ref", description="desc", order_id=OrderID(99)),
        )


def test_reference_orders_loads_orders_in_reference_order():
    run, *_ = build_worked_run(with_print=False, with_laminate=False, with_cut=False)
    first = Order(
        id=OrderID(1),
        product=Product(blocks=(run.block,), operations=()),
        count=1,
        description="",
        created_at=TEST_ORDER_CREATED_AT,
    )
    second = Order(
        id=OrderID(2),
        product=Product(blocks=(run.block,), operations=()),
        count=2,
        description="",
        created_at=TEST_ORDER_CREATED_AT,
    )
    orders = InMemoryOrderRepository(orders={first.id: first, second.id: second})
    refs = InMemoryReferenceRepository()
    refs.save(Reference(name="b", description="", order_id=second.id))
    refs.save(Reference(name="a", description="", order_id=first.id))

    loaded = _service(orders=orders, references=refs).reference_orders()

    assert loaded == (second, first)
