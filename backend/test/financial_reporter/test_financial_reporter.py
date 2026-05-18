from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from backend.models.order import Order, OrderCostReport, Economy
from backend.models.status import Status
from backend.financial_reporter.financial_reporter import (
    FinancialReporter,
    FinancialReporterError,
)


def _create_order(
    revenue: Decimal,
    profit: Decimal,
    unit_cost: Decimal = Decimal("10"),
    unit_price: Decimal = Decimal("20"),
    markup: Decimal = Decimal("0.2"),
    units: int = 10,
    date: datetime | None = None,
) -> Order:
    cost_report = OrderCostReport(
        unit_cost_price=unit_cost,
        unit_cost=unit_price,
        edition_cost=revenue,
        profit_after_tax=profit,
        printing_cost_reports=[],
    )

    return Order(
        id=1,
        creation_date=date or datetime.now(),
        status=Status.SAVED,
        unit_count=units,
        cost_report=cost_report,
        printings=[],
        operations=[],
        economy=Economy(
            tax_rate=Decimal("0.93"),
            markup=markup,
        ),
    )


def test_empty_orders_raises():
    with pytest.raises(FinancialReporterError):
        FinancialReporter([]).get_report()


def test_period_calculation():
    now = datetime.now()
    order1 = _create_order(
        Decimal("100"),
        Decimal("20"),
        date=now - timedelta(days=1),
    )
    order2 = _create_order(
        Decimal("200"),
        Decimal("50"),
        date=now,
    )

    report = FinancialReporter([order1, order2]).get_report()

    assert report.period.start_date == order1.creation_date
    assert report.period.end_date == order2.creation_date


def test_revenue_calculation():
    order1 = _create_order(Decimal("100"), Decimal("20"))
    order2 = _create_order(Decimal("200"), Decimal("50"))

    report = FinancialReporter([order1, order2]).get_report()

    assert report.revenue.total_revenue == Decimal("300")
    assert report.revenue.total_profit_after_tax == Decimal("70")
    assert report.revenue.total_cost_price == Decimal("230")


def test_average_metrics():
    order1 = _create_order(Decimal("100"), Decimal("20"))
    order2 = _create_order(Decimal("200"), Decimal("40"))

    report = FinancialReporter([order1, order2]).get_report()

    assert report.revenue.average_order_value == Decimal("150")
    assert report.revenue.average_profit_per_order == Decimal("30")


def test_margin_calculation():
    order = _create_order(Decimal("100"), Decimal("20"))

    report = FinancialReporter([order]).get_report()

    assert report.margin.gross_margin == Decimal("20")
    assert report.margin.net_margin == Decimal("20")


def test_unit_economics():
    order1 = _create_order(
        Decimal("100"),
        Decimal("20"),
        unit_cost=Decimal("10"),
        unit_price=Decimal("20"),
        units=10,
    )
    order2 = _create_order(
        Decimal("200"),
        Decimal("40"),
        unit_cost=Decimal("20"),
        unit_price=Decimal("40"),
        units=10,
    )

    report = FinancialReporter([order1, order2]).get_report()

    assert report.unit_economics.average_unit_cost_price == Decimal("1.5")
    assert report.unit_economics.average_unit_price == Decimal("3")
    assert report.unit_economics.average_profit_per_unit == Decimal("1.5")


def test_orders_stats():
    order1 = _create_order(Decimal("100"), Decimal("20"))
    order2 = _create_order(Decimal("100"), Decimal("-10"))

    report = FinancialReporter([order1, order2]).get_report()

    assert report.orders.total_orders == 2
    assert report.orders.profitable_orders == 1
    assert report.orders.unprofitable_orders == 1
    assert report.orders.best_order_profit == Decimal("20")
    assert report.orders.worst_order_profit == Decimal("-10")


def test_tax_metrics_zero():
    order = _create_order(Decimal("100"), Decimal("20"))

    report = FinancialReporter([order]).get_report()

    assert report.tax.total_tax == Decimal("0")
    assert report.tax.effective_tax_rate == Decimal("0")


def test_average_markup():
    order1 = _create_order(
        Decimal("100"),
        Decimal("20"),
        markup=Decimal("0.1"),
    )
    order2 = _create_order(
        Decimal("100"),
        Decimal("20"),
        markup=Decimal("0.3"),
    )

    report = FinancialReporter([order1, order2]).get_report()

    assert report.margin.average_markup == Decimal("0.2")
