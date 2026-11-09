"""Shared assertions and product builders for storage tests."""

from __future__ import annotations

from decimal import Decimal

from backend.new_core import AdditionalWork, Order, Product
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.values.money import Money
from backend.new_core.values.percent import Percent


def product_from_run(run: PrintRun) -> Product:
    return Product(
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
