"""Behavior of order quote and save use cases."""

# pylint: disable=protected-access

from dataclasses import dataclass, field, replace
from decimal import Decimal

import pytest

from backend.new_core import AdditionalWork, InvalidInput, Percent, RunEstimate
from backend.new_core.accountant.accountant import Accountant
from backend.new_core.accountant.order_report import OrderReport
from backend.new_core.accountant.pricing.factory import PricingStrategyFactory
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.part import Part
from backend.new_core.materials.film import FilmID
from backend.new_core.materials.sheet import SheetID
from backend.new_core.order.factory import OrderFactory
from backend.new_core.order.order import Order, OrderContent, OrderID
from backend.new_core.order.product import Product
from backend.new_core.application_services.order import (
    OrderIdAllocationFailed,
    OrderService,
)
from backend.new_core.print_run.factory import PrintRunFactory
from backend.new_core.print_run.print_run import PrintRun, PrintRunID
from backend.new_core.values.money import Money
from backend.test.new_core.in_memory_repositories import (
    InMemoryCutterOperatorRepository,
    InMemoryCutterRepository,
    InMemoryDieCutterOperatorRepository,
    InMemoryFilmRepository,
    InMemoryLaminatorOperatorRepository,
    InMemoryLaminatorRepository,
    InMemoryOrderRepository,
    InMemoryPressOperatorRepository,
    InMemoryPrinterRepository,
    InMemoryUnitOfWork,
)
from backend.test.new_core.test_print_run import (
    build_worked_run,
    order_service,
    pricing_strategy_factory,
)
from backend.test.storage.helpers import TEST_ORDER_CREATED_AT


def _create_service(uow: InMemoryUnitOfWork, ctx) -> OrderService:
    return order_service(uow, ctx)


def _block_with_spacing(block: Part, spacing: int, ctx) -> Part:
    sheet = ctx.sheets[block.imposition.press_sheet.id]
    imposition = replace(
        block.imposition,
        spacing=spacing,
        press_sheet=sheet,
    )
    return replace(block, imposition=imposition, need_spacing=False)


def _product_from_run(
    run,
    *,
    extra_block=None,
    parts_markup: Percent = Percent(0),
) -> Product:
    blocks = (run.block,) if extra_block is None else (run.block, extra_block)
    return Product(
        parts_markup=parts_markup,
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


def test_save_persists_imposition_spacing_from_product():
    """Save stores imposition spacing from the product block."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)
    block = _block_with_spacing(run.block, 5, ctx)
    product = Product(parts_markup=Percent(0), blocks=(block,), operations=())

    order = OrderFactory(uow.orders).create(product, count=1)
    runs = service._made_run_for_order(order)
    assert runs[0].block.imposition.spacing == 5

    order_id = service.save(product, count=1)
    stored_runs = uow.print_runs.take_all_for_order(order_id)
    assert stored_runs[0].block.imposition.spacing == 5


def test_order_report_keeps_stored_spacing_when_catalog_printer_changes():
    """order_report does not overwrite spacing from the updated printer catalog."""
    run, printing, _, _, ctx = build_worked_run()
    printer_id = printing.printer_id
    ctx.printers[printer_id] = replace(ctx.printers[printer_id], spacing=5)
    printers = InMemoryPrinterRepository(items=dict(ctx.printers))
    uow = InMemoryUnitOfWork()
    service = OrderService(
        uow=uow,
        order_factory=OrderFactory(uow.orders),
        print_run_factory=PrintRunFactory(uow.print_runs),
        pricing_factory=PricingStrategyFactory(
            printers,
            InMemoryPressOperatorRepository(items=dict(ctx.press_operators)),
            InMemoryLaminatorRepository(items=dict(ctx.laminators)),
            InMemoryLaminatorOperatorRepository(
                items=dict(ctx.laminator_operators),
            ),
            InMemoryCutterRepository(items=dict(ctx.cutters)),
            InMemoryCutterOperatorRepository(
                items=dict(ctx.cutter_operators),
            ),
            InMemoryDieCutterOperatorRepository(
                items=dict(ctx.die_cut_operators),
            ),
            InMemoryFilmRepository(items=dict(ctx.films)),
        ),
    )
    product = Product(
        parts_markup=Percent(0),
        blocks=(_block_with_spacing(run.block, 5, ctx),),
        operations=(),
    )
    order_id = service.save(product, count=1)
    before = service.order_report(order_id)
    printers.items[printer_id] = replace(printers.items[printer_id], spacing=99)

    stored = uow.print_runs.take_all_for_order(order_id)[0]
    assert stored.block.imposition.spacing == 5
    assert service.order_report(order_id).impositions == before.impositions


def test_replace_stores_imposition_spacing_from_product():
    """Replace keeps imposition spacing from the new product."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)
    product = _product_from_run(run)

    order_id = service.save(product, count=1)
    updated = Product(
        parts_markup=Percent(0),
        blocks=(_block_with_spacing(run.block, 5, ctx),),
        operations=(),
    )
    service.replace(order_id, OrderContent(product=updated, count=2))

    runs = uow.print_runs.take_all_for_order(order_id)
    assert runs[0].block.imposition.spacing == 5


def test_quote_returns_report_and_does_not_write_stores():
    """Quote prices the product and leaves order and print-run maps empty."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)
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
        sheet_id=SheetID(2),
    )
    for repo, other in ((ctx, ctx2), (ctx2, ctx)):
        repo.printers.update(other.printers)
        repo.press_operators.update(other.press_operators)
        repo.laminators.update(other.laminators)
        repo.laminator_operators.update(other.laminator_operators)
        repo.cutters.update(other.cutters)
        repo.cutter_operators.update(other.cutter_operators)
        repo.sheets.update(other.sheets)
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)
    product = _product_from_run(run, extra_block=run2.block)

    report = service.quote(product, count=1)

    assert report.impositions == (6, 12)


def test_quote_applies_product_parts_markup_to_each_block():
    """One ``parts_markup`` prices every print run like a single-block product."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)
    markup = Percent(10)
    accountant = Accountant()

    def sheet_markups(blocks: tuple) -> tuple:
        product = Product(parts_markup=markup, blocks=blocks, operations=())
        order = OrderFactory(uow.orders).create(product, count=4)
        runs = service._made_run_for_order(order)
        return tuple(
            accountant.sheet_cost_report(
                service._run_estimate(r, order.product.parts_markup),
            ).markup
            for r in runs
        )

    reference = sheet_markups((run.block,))[0]
    for block_markup in sheet_markups((run.block, run.block)):
        assert block_markup == reference


def test_quote_with_missing_printer_raises_and_leaves_stores_empty():
    """A missing printer id raises KeyError and does not write stores."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)
    broken = run.block.operations[0]

    bad_block = replace(
        run.block,
        operations=(
            replace(broken, printer_id=PrinterID(999)),
        ),
    )
    product = Product(parts_markup=Percent(0), blocks=(bad_block,), operations=())

    with pytest.raises(KeyError):
        service.quote(product, count=4)

    assert not uow.orders.orders
    assert not uow.print_runs.by_order


def test_quote_with_missing_film_raises_and_leaves_stores_empty():
    """A missing film id raises KeyError and does not write stores."""
    run, _, laminate, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)

    bad_laminate = replace(laminate, film_id=FilmID(999))
    bad_block = replace(
        run.block,
        operations=tuple(
            bad_laminate if op is laminate else op for op in run.block.operations
        ),
    )
    product = Product(parts_markup=Percent(0), blocks=(bad_block,), operations=())

    with pytest.raises(KeyError):
        service.quote(product, count=4)

    assert not uow.orders.orders
    assert not uow.print_runs.by_order


def test_save_persists_order_and_runs():
    """Save returns an order id and stores the order with all runs."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)
    product = _product_from_run(run)

    order_id = service.save(product, count=4, description="буклет")

    stored = uow.orders.take(order_id)
    assert stored.count == 4
    assert stored.description == "буклет"
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
        repo.cutters.update(other.cutters)
        repo.cutter_operators.update(other.cutter_operators)
        repo.sheets.update(other.sheets)
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)
    product = _product_from_run(run, extra_block=run2.block)
    order_count = 2

    order_id = service.save(product, count=order_count)
    runs = uow.print_runs.take_all_for_order(order_id)

    assert len(runs) == 2
    assert runs[0].block.imposition.press_sheet.id == product.blocks[0].imposition.press_sheet.id
    assert runs[1].block.imposition.press_sheet.id == product.blocks[1].imposition.press_sheet.id
    assert runs[0].required_count == order_count * product.blocks[0].count
    assert runs[1].required_count == order_count * product.blocks[1].count


def test_two_orders_may_share_the_same_print_run_id_value():
    """Print run ids are scoped per order; two orders can both use PrintRunID(0)."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)
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
        description="",
        created_at=TEST_ORDER_CREATED_AT,
    )
    orders = _SeededOrderRepository(
        orders={OrderID(1): existing},
        preset=[1, 2],
    )
    uow = InMemoryUnitOfWork(orders=orders)
    service = _create_service(uow, ctx)

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
        description="",
        created_at=TEST_ORDER_CREATED_AT,
    )
    orders = _AlwaysOccupiedOrderRepository(
        orders={OrderID(1): seed},
        fixed_id=1,
    )
    uow = InMemoryUnitOfWork(orders=orders)
    service = _create_service(uow, ctx)

    with pytest.raises(OrderIdAllocationFailed) as exc_info:
        service.save(_product_from_run(run), count=4)

    assert exc_info.value.last_occupied == OrderID(1)
    assert len(uow.orders.orders) == 1
    assert OrderID(1) in uow.orders.orders
    assert not uow.print_runs.by_order


def test_build_run_estimate_rejects_unknown_operation():
    """An unsupported operation type raises TypeError from build_run_estimate."""
    run, _, _, _, ctx = build_worked_run()

    class _UnknownOperation:  # pylint: disable=too-few-public-methods
        pass

    broken = PrintRun(
        id=run.id,
        for_order=run.for_order,
        block=replace(run.block, operations=(_UnknownOperation(),)),
        required_count=run.required_count,
    )

    with pytest.raises(TypeError, match="Unsupported run operation"):
        strategies = [
            pricing_strategy_factory(ctx).create(operation, run)
            for operation in broken.block.operations
        ]
        return RunEstimate.create(strategies, run=run)


def test_replace_keeps_created_at_and_updates_description():
    """Replace updates description and count but keeps the original created_at."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)
    product = _product_from_run(run)

    order_id = service.save(product, count=4, description="старое")
    created_at = uow.orders.take(order_id).created_at

    service.replace(
        order_id,
        OrderContent(product=product, count=8, description="новое"),
    )
    stored = uow.orders.take(order_id)

    assert stored.count == 8
    assert stored.description == "новое"
    assert stored.created_at == created_at


def test_save_does_not_retry_on_invalid_input():
    """InvalidInput during assemble does not retry and leaves stores empty."""
    run, _, _, _, ctx = build_worked_run()
    uow = InMemoryUnitOfWork()
    service = _create_service(uow, ctx)
    product = _product_from_run(run)

    with pytest.raises(InvalidInput):
        service.save(product, count=0)

    assert not uow.orders.orders
    assert not uow.print_runs.by_order
