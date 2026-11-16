"""Shared assertions and product builders for storage tests."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal

from backend.new_core import AdditionalWork, Order, Part, Product
from backend.new_core.equipment.printer import Printer, PrinterID, PrinterPrices
from backend.new_core.order.order import OrderContent, OrderID
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.values.money import Money
from backend.new_core.values.percent import Percent

__all__ = [
    "TEST_ORDER_CREATED_AT",
    "make_order",
    "assembly_additional_work",
    "zero_printer_prices",
    "sequential_printer_prices",
    "sample_printer",
    "product_from_run",
    "assert_print_run_equal",
]

TEST_ORDER_CREATED_AT = datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC)


def make_order(
    order_id: int,
    content: OrderContent,
    *,
    created_at: datetime = TEST_ORDER_CREATED_AT,
) -> Order:
    return Order(
        id=OrderID(order_id),
        product=content.product,
        count=content.count,
        description=content.description,
        created_at=created_at,
    )


def assembly_additional_work(
    *,
    price: Decimal = Decimal(999),
    markup: Percent = Percent(0),
) -> AdditionalWork:
    return AdditionalWork(
        name="сборка",
        price=Money(price),
        description="склейка",
        markup=markup,
    )


def zero_printer_prices() -> PrinterPrices:
    zero = Money(Decimal(0))
    return PrinterPrices(
        startup=zero,
        cyan=zero,
        magenta=zero,
        yellow=zero,
        black=zero,
    )


def sequential_printer_prices() -> PrinterPrices:
    return PrinterPrices(
        startup=Money(Decimal("1")),
        cyan=Money(Decimal("2")),
        magenta=Money(Decimal("3")),
        yellow=Money(Decimal("4")),
        black=Money(Decimal("5")),
    )


def sample_printer(
    printer_id: int,
    name: str,
    spacing: int,
    *,
    prices: PrinterPrices | None = None,
) -> Printer:
    return Printer(
        id=PrinterID(printer_id),
        name=name,
        spacing=spacing,
        prices=prices or sequential_printer_prices(),
    )


def product_from_run(
    run: PrintRun,
    *,
    extra_block: Part | None = None,
    parts_markup: Percent = Percent(0),
    strip_spacing: bool = True,
) -> Product:
    block = (
        replace(run.block, need_spacing=False)
        if strip_spacing
        else run.block
    )
    blocks = (block,) if extra_block is None else (block, extra_block)
    return Product(
        parts_markup=parts_markup,
        blocks=blocks,
        operations=(assembly_additional_work(),),
    )


def assert_print_run_equal(stored: PrintRun, expected: PrintRun) -> None:
    assert stored.id == expected.id
    assert stored.for_order == expected.for_order
    assert stored.required_count == expected.required_count
    assert stored.block == replace(expected.block, need_spacing=False)
