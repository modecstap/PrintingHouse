"""Shared assertions and product builders for storage tests."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from backend.new_core import AdditionalWork, Order, Product
from backend.new_core.order.order import OrderID
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.values.money import Money
from backend.new_core.values.percent import Percent

TEST_ORDER_CREATED_AT = datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC)


def make_order(
    order_id: int,
    product: Product,
    count: int,
    *,
    description: str = "",
    created_at: datetime = TEST_ORDER_CREATED_AT,
) -> Order:
    return Order(
        id=OrderID(order_id),
        product=product,
        count=count,
        description=description,
        created_at=created_at,
    )


def product_from_run(run: PrintRun, *, parts_markup: Percent = Percent(0)) -> Product:
    return Product(
        parts_markup=parts_markup,
        blocks=(run.block,),
        operations=(
            AdditionalWork(
                name="сборка",
                price=Money(Decimal(999)),
                description="склейка",
                markup=Percent(0),
            ),
        ),
    )


def assert_print_run_equal(stored: PrintRun, expected: PrintRun) -> None:
    assert stored.id == expected.id
    assert stored.for_order == expected.for_order
    assert stored.required_count == expected.required_count
    assert stored.block == expected.block
