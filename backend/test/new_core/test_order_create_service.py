"""Behavior of order quote and save use cases."""

from dataclasses import dataclass, field
from decimal import Decimal

import pytest

from backend.new_core import AdditionalWork, InvalidInput, Percent
from backend.new_core.accountant.order_report import OrderReport
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.product import Product
from backend.new_core.order.service import OrderIdAllocationFailed, OrderService
from backend.new_core.print_run.print_run import PrintRunID
from backend.new_core.values.money import Money
from backend.test.new_core.in_memory_repositories import (
    InMemoryCutterOperatorRepository,
    InMemoryDieCutterOperatorRepository,
    InMemoryLaminatorOperatorRepository,
    InMemoryLaminatorRepository,
    InMemoryOrderRepository,
    InMemoryPressOperatorRepository,
    InMemoryPrinterRepository,
    InMemoryPrintRunRepository,
    InMemoryUnitOfWork,
)
from backend.test.new_core.test_print_run import build_worked_run


def _create_service(
    uow: InMemoryUnitOfWork,
    run,
    ctx,
) -> OrderService:
    return OrderService(
        uow=uow,
        printers=InMemoryPrinterRepository(items=dict(ctx.printers)),
        press_operators=InMemoryPressOperatorRepository(
            items=dict(ctx.press_operators),
        ),
        laminators=InMemoryLaminatorRepository(items=dict(ctx.laminators)),
        laminator_operators=InMemoryLaminatorOperatorRepository(
            items=dict(ctx.laminator_operators),
        ),
        cutter_operators=InMemoryCutterOperatorRepository(
            items=dict(ctx.cutter_operators),
        ),
        die_cut_operators=InMemoryDieCutterOperatorRepository(
            items=dict(ctx.die_cut_operators),
        ),
    )


def _product_from_run(run, *, extra_block=None) -> Product:
    blocks = (run.block,) if extra_block is None else (run.block, extra_block)
    return Product(
        blocks=blocks,
        operations=(
            AdditionalWork(
                name="сборка",
                price=Money(Decimal(999)),
                description="склейка",
                markup=Percent(0),
            ),
        ),
    )


def test_quote_returns_report_and_does_not_write_stores():
    """Quote prices the product and leaves order and print-run maps empty."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, run, ctx)
    product = _product_from_run(run)

    report = service.quote(product, count=4)

    assert isinstance(report, OrderReport)
    assert not uow.orders.orders
    assert not uow.print_runs.by_order
    assert report.impositions == (6,)


def test_quote_with_two_blocks_reports_two_imposition_counts():
    """Two blocks yield two imposition counts in block order."""
    run, _, _, _, ctx = build_worked_run(
        target_width=10,
        target_height=20,
        press_width=30,
        press_height=40,
    )
    run2, _, _, _, ctx2 = build_worked_run(
        target_width=10,
        target_height=20,
        press_width=60,
        press_height=40,
    )
    for repo, other in ((ctx, ctx2), (ctx2, ctx)):
        repo.printers.update(other.printers)
        repo.press_operators.update(other.press_operators)
        repo.laminators.update(other.laminators)
        repo.laminator_operators.update(other.laminator_operators)
        repo.cutter_operators.update(other.cutter_operators)
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, run, ctx)
    product = _product_from_run(run, extra_block=run2.block)

    report = service.quote(product, count=1)

    assert report.impositions == (6, 12)


def test_quote_with_missing_printer_raises_and_leaves_stores_empty():
    """A missing printer id raises KeyError and does not write stores."""
    run, printing, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, run, ctx)
    broken = run.block.operations[0]
    from dataclasses import replace

    bad_block = replace(
        run.block,
        operations=(
            replace(broken, printer_id=PrinterID(999)),
        ),
    )
    product = Product(blocks=(bad_block,), operations=())

    with pytest.raises(KeyError):
        service.quote(product, count=4)

    assert not uow.orders.orders
    assert not uow.print_runs.by_order


def test_save_persists_order_and_runs():
    """Save returns an order id and stores the order with all runs."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, run, ctx)
    product = _product_from_run(run)

    order_id = service.save(product, count=4)

    stored = uow.orders.take(order_id)
    assert stored.count == 4
    runs = uow.print_runs.take_all_for_order(order_id)
    assert len(runs) == 1
    assert runs[0].for_order == order_id
    assert runs[0].required_count == 4 * run.block.count


def test_save_maps_each_block_to_one_run_in_order():
    """Each block becomes one run with required_count order.count times block.count."""
    run, _, _, _, ctx = build_worked_run()
    run2, _, _, _, ctx2 = build_worked_run(required_count=5)
    for repo, other in ((ctx, ctx2), (ctx2, ctx)):
        repo.printers.update(other.printers)
        repo.press_operators.update(other.press_operators)
        repo.laminators.update(other.laminators)
        repo.laminator_operators.update(other.laminator_operators)
        repo.cutter_operators.update(other.cutter_operators)
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, run, ctx)
    product = _product_from_run(run, extra_block=run2.block)
    order_count = 2

    order_id = service.save(product, count=order_count)
    runs = uow.print_runs.take_all_for_order(order_id)

    assert len(runs) == 2
    assert runs[0].block is product.blocks[0]
    assert runs[1].block is product.blocks[1]
    assert runs[0].required_count == order_count * product.blocks[0].count
    assert runs[1].required_count == order_count * product.blocks[1].count


def test_two_orders_may_share_the_same_print_run_id_value():
    """Print run ids are scoped per order; two orders can both use PrintRunID(0)."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, run, ctx)
    product = _product_from_run(run)

    first_id = service.save(product, count=4)
    second_id = service.save(product, count=4)
    first_runs = uow.print_runs.take_all_for_order(first_id)
    second_runs = uow.print_runs.take_all_for_order(second_id)

    assert first_runs[0].id == PrintRunID(0)
    assert second_runs[0].id == PrintRunID(0)
    assert first_runs[0].for_order != second_runs[0].for_order


@dataclass
class _SeededOrderRepository(InMemoryOrderRepository):
    """Returns preset ids then falls back to the base counter."""

    preset: list[int] = field(default_factory=list)

    def generate_id(self) -> OrderID:
        if self.preset:
            return OrderID(self.preset.pop(0))
        return super().generate_id()


def test_save_retries_on_occupied_order_id():
    """Save retries with a new id when the first allocated id is already stored."""
    run, _, _, _, ctx = build_worked_run()
    existing = Order(
        id=OrderID(1),
        product=_product_from_run(run),
        count=1,
    )
    orders = _SeededOrderRepository(
        orders={OrderID(1): existing},
        preset=[1, 2],
    )
    uow = InMemoryUnitOfWork(orders=orders)
    service = _create_service(uow, run, ctx)

    order_id = service.save(_product_from_run(run), count=4)

    assert order_id == OrderID(2)
    assert OrderID(1) in uow.orders.orders
    assert uow.orders.take(order_id).count == 4


@dataclass
class _AlwaysOccupiedOrderRepository(InMemoryOrderRepository):
    """Always returns the same occupied id."""

    fixed_id: int = 1

    def generate_id(self) -> OrderID:
        return OrderID(self.fixed_id)


def test_save_raises_after_three_occupied_ids():
    """Three occupied ids yield OrderIdAllocationFailed and empty maps except the seed."""
    run, _, _, _, ctx = build_worked_run()
    seed = Order(
        id=OrderID(1),
        product=_product_from_run(run),
        count=1,
    )
    orders = _AlwaysOccupiedOrderRepository(
        orders={OrderID(1): seed},
        fixed_id=1,
    )
    uow = InMemoryUnitOfWork(orders=orders)
    service = _create_service(uow, run, ctx)

    with pytest.raises(OrderIdAllocationFailed) as exc_info:
        service.save(_product_from_run(run), count=4)

    assert exc_info.value.last_occupied == OrderID(1)
    assert len(uow.orders.orders) == 1
    assert OrderID(1) in uow.orders.orders
    assert not uow.print_runs.by_order


def test_save_does_not_retry_on_invalid_input():
    """InvalidInput during assemble does not retry and leaves stores empty."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, run, ctx)
    product = _product_from_run(run)

    with pytest.raises(InvalidInput):
        service.save(product, count=0)

    assert not uow.orders.orders
    assert not uow.print_runs.by_order
