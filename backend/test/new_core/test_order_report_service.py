"""Behavior of order report use case."""

from dataclasses import replace
from decimal import Decimal

import pytest

from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.product import Product
from backend.new_core.order.repository import OrderNotFound
from backend.new_core.application_services.order import OrderService
from backend.new_core.values.money import Money
from backend.new_core.values.percent import Percent
from backend.test.new_core.in_memory_repositories import (
    InMemoryFilmRepository,
    InMemoryOrderRepository,
    InMemoryPrintRunRepository,
    InMemorySheetRepository,
    InMemoryUnitOfWork,
)
from backend.test.new_core.test_print_run import (
    assert_tax_scaling_report_prices,
    attach_die_cut_operator,
    build_run_without_block_operations,
    build_worked_run,
    order_service,
    tax_scaling_order,
)
from backend.test.storage.helpers import TEST_ORDER_CREATED_AT


def _service_from_fixtures(run, ctx) -> OrderService:
    return order_service(InMemoryUnitOfWork(), ctx)


def test_order_report_scales_the_product_by_tax_and_the_order_count():
    """Work of 100 with 10 percent markup is 110.

    Then times 100/93, then times 4.

    The run has no operations, so its block report is zero. Income equals
    the order price because material and startup stay zero.
    """
    run, _, _, _, ctx = build_run_without_block_operations()
    order = tax_scaling_order(run)

    orders = InMemoryOrderRepository(orders={order.id: order})
    print_runs = InMemoryPrintRunRepository(by_order={order.id: (run,)})
    service = order_service(
        InMemoryUnitOfWork(orders=orders, print_runs=print_runs),
        ctx,
    )

    report = service.order_report(order.id)

    assert_tax_scaling_report_prices(report)


def test_order_report_prices_die_cut_through_order_service():
    """OrderService builds a DieCut estimate when pricing a stored run."""
    run, _, _, _, ctx = build_run_without_block_operations()
    attach_die_cut_operator(run, ctx)
    order = Order(
        id=OrderID(5),
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
    uow = InMemoryUnitOfWork(
        orders=InMemoryOrderRepository(orders={order.id: order}),
        print_runs=InMemoryPrintRunRepository(by_order={order.id: (run,)}),
    )
    service = order_service(uow, ctx)

    plain = build_run_without_block_operations()
    plain_run = plain[0]
    plain_product = Product(
        parts_markup=Percent(0),
        blocks=(plain_run.block,),
        operations=(),
    )
    plain_order = Order(
        id=OrderID(6),
        product=plain_product,
        count=1,
        description="",
        created_at=TEST_ORDER_CREATED_AT,
    )
    plain_uow = InMemoryUnitOfWork(
        orders=InMemoryOrderRepository(orders={plain_order.id: plain_order}),
        print_runs=InMemoryPrintRunRepository(
            by_order={plain_order.id: (plain_run,)},
        ),
    )
    plain_report = order_service(
        plain_uow,
        plain[4]).order_report(
        plain_order.id)

    report = service.order_report(order.id)
    assert report.order_price.amount > plain_report.order_price.amount


def test_order_report_keeps_stored_sheet_price_after_catalog_replace():
    """Report prices paper from the stored run, not live catalog sheet rows."""
    run, _, _, _, ctx = build_worked_run(with_laminate=False)
    sheets = InMemorySheetRepository(items=dict(ctx.sheets))
    uow = InMemoryUnitOfWork()
    service = order_service(uow, ctx)
    product = Product(
        parts_markup=Percent(0), blocks=(
            run.block,), operations=())
    order_id = service.save(product, count=1)
    before = service.order_report(order_id)
    sheet = sheets.take(run.block.imposition.press_sheet.id)
    sheets.replace(
        replace(
            sheet,
            paper=replace(
                sheet.paper,
                price_per_kilo=Money(Decimal(50_000)),
            ),
        ),
    )
    after = service.order_report(order_id)
    assert after.order_price.amount == before.order_price.amount


def test_order_report_reflects_catalog_film_replace_after_save():
    """After PUT on the film catalog, report uses the new film price."""
    run, _, laminate, _, ctx = build_worked_run(
        with_print=False,
        with_cut=False,
    )
    films = InMemoryFilmRepository(items=dict(ctx.films))
    uow = InMemoryUnitOfWork()
    service = order_service(uow, ctx, films=films)
    product = Product(
        parts_markup=Percent(0), blocks=(
            run.block,), operations=())
    order_id = service.save(product, count=1)
    before = service.order_report(order_id)
    film = films.take(laminate.film_id)
    films.replace(replace(film, price=Money(Decimal(500))))
    after = service.order_report(order_id)
    assert after.order_price.amount > before.order_price.amount


def test_order_report_raises_when_order_is_missing():
    """An unknown order id raises OrderNotFound from the order repository."""
    run, _, _, _, ctx = build_run_without_block_operations()
    service = _service_from_fixtures(run, ctx)

    with pytest.raises(OrderNotFound):
        service.order_report(OrderID(999))
