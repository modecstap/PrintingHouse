"""Behavior of order report use case."""

from decimal import Decimal

import pytest

from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.product import Product
from backend.new_core.order.repository import OrderNotFound
from backend.new_core.application_services.order import OrderService
from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.test.new_core.test_print_run import _append_block_operation
from backend.new_core.values.money import Money
from backend.new_core.values.percent import Percent
from backend.new_core import AdditionalWork, Accountant
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
    InMemoryPrintRunRepository,
    InMemoryUnitOfWork,
)
from backend.test.new_core.test_print_run import build_worked_run


def _service_from_fixtures(run, ctx) -> OrderService:
    return OrderService(
        uow=InMemoryUnitOfWork(),
        printers=InMemoryPrinterRepository(items=dict(ctx.printers)),
        press_operators=InMemoryPressOperatorRepository(
            items=dict(ctx.press_operators),
        ),
        laminators=InMemoryLaminatorRepository(items=dict(ctx.laminators)),
        laminator_operators=InMemoryLaminatorOperatorRepository(
            items=dict(ctx.laminator_operators),
        ),
        cutters=InMemoryCutterRepository(items=dict(ctx.cutters)),
        cutter_operators=InMemoryCutterOperatorRepository(
            items=dict(ctx.cutter_operators),
        ),
        die_cut_operators=InMemoryDieCutterOperatorRepository(
            items=dict(ctx.die_cut_operators),
        ),
        films=InMemoryFilmRepository(items=dict(ctx.films)),
    )


def test_order_report_scales_the_product_by_tax_and_the_order_count():
    """Work of 100 with 10 percent markup is 110, then times 100/93, then times 4.

    The run has no operations, so its block report is zero. Income equals
    the order price because material and startup stay zero.
    """
    run, _, _, _, ctx = build_worked_run(
        with_print=False,
        with_laminate=False,
        with_cut=False,
    )
    order = Order(
        id=OrderID(1),
        product=Product(
            blocks=(run.block,),
            operations=(
                AdditionalWork(
                    name="сборка",
                    price=Money(Decimal(100)),
                    description="склейка",
                    markup=Percent(10),
                ),
            ),
        ),
        count=4,
    )

    orders = InMemoryOrderRepository(orders={order.id: order})
    print_runs = InMemoryPrintRunRepository(by_order={order.id: (run,)})
    service = OrderService(
        uow=InMemoryUnitOfWork(orders=orders, print_runs=print_runs),
        printers=InMemoryPrinterRepository(items=dict(ctx.printers)),
        press_operators=InMemoryPressOperatorRepository(
            items=dict(ctx.press_operators),
        ),
        laminators=InMemoryLaminatorRepository(items=dict(ctx.laminators)),
        laminator_operators=InMemoryLaminatorOperatorRepository(
            items=dict(ctx.laminator_operators),
        ),
        cutters=InMemoryCutterRepository(items=dict(ctx.cutters)),
        cutter_operators=InMemoryCutterOperatorRepository(
            items=dict(ctx.cutter_operators),
        ),
        die_cut_operators=InMemoryDieCutterOperatorRepository(
            items=dict(ctx.die_cut_operators),
        ),
        films=InMemoryFilmRepository(items=dict(ctx.films)),
    )

    report = service.order_report(order.id)
    accountant = Accountant()
    estimate = service._run_estimate(run)
    priced = accountant.order_cost_report(
        [estimate],
        order.product.operations,
        order,
    )

    compensation = Decimal(100) / Decimal(93)
    assert priced.work == Money(Decimal(400))
    assert priced.markup == Money(Decimal(40))
    assert priced.total() == Money(Decimal(440))
    assert report.product_price == (
        Money(Decimal(100) * compensation) + Money(Decimal(10) * compensation)
    )
    assert report.order_price == (
        Money(Decimal(400) * compensation) + Money(Decimal(40) * compensation)
    )
    assert report.income == report.order_price
    assert report.impositions == (6,)


def test_order_report_prices_die_cut_through_order_service():
    """OrderService builds a DieCut estimate when pricing a stored run."""
    run, _, _, _, ctx = build_worked_run(
        with_print=False,
        with_laminate=False,
        with_cut=False,
    )
    die_operator = DieCutterOperator(
        id=DieCutterOperatorID(2),
        salary_by_operation=Money(Decimal(8)),
    )
    _append_block_operation(run, DieCut(operator_id=die_operator.id))
    ctx.die_cut_operators[die_operator.id] = die_operator
    order = Order(
        id=OrderID(5),
        product=Product(blocks=(run.block,), operations=()),
        count=1,
    )
    uow = InMemoryUnitOfWork(
        orders=InMemoryOrderRepository(orders={order.id: order}),
        print_runs=InMemoryPrintRunRepository(by_order={order.id: (run,)}),
    )
    service = OrderService(
        uow=uow,
        printers=InMemoryPrinterRepository(items=dict(ctx.printers)),
        press_operators=InMemoryPressOperatorRepository(
            items=dict(ctx.press_operators),
        ),
        laminators=InMemoryLaminatorRepository(items=dict(ctx.laminators)),
        laminator_operators=InMemoryLaminatorOperatorRepository(
            items=dict(ctx.laminator_operators),
        ),
        cutters=InMemoryCutterRepository(items=dict(ctx.cutters)),
        cutter_operators=InMemoryCutterOperatorRepository(
            items=dict(ctx.cutter_operators),
        ),
        die_cut_operators=InMemoryDieCutterOperatorRepository(
            items=dict(ctx.die_cut_operators),
        ),
        films=InMemoryFilmRepository(items=dict(ctx.films)),
    )

    estimate = service._run_estimate(run)

    assert estimate.aggregated_operations().work == Money(Decimal(8))


def test_order_report_raises_when_order_is_missing():
    """An unknown order id raises OrderNotFound from the order repository."""
    run, _, _, _, ctx = build_worked_run(
        with_print=False,
        with_laminate=False,
        with_cut=False,
    )
    service = _service_from_fixtures(run, ctx)

    with pytest.raises(OrderNotFound):
        service.order_report(OrderID(999))
