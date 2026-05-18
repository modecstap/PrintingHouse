from datetime import timezone
from decimal import Decimal

from backend.models.order import Order
from backend.models.financial_report import (
    FinancialReport,
    ReportPeriod,
    RevenueMetrics,
    MarginMetrics,
    UnitEconomics,
    OrdersStats,
    TaxMetrics,
)


class FinancialReporterError(Exception):
    """Базовая ошибка построения финансового отчёта."""


class FinancialReporter:
    def __init__(self, orders: list[Order]) -> None:
        """
        initialize builder

        :param orders: список заказов
        """
        self._orders = orders or []
        self._active_orders = self._orders

    def build(self, period: ReportPeriod) -> FinancialReport:
        """
        build financial report for selected period

        :param period: период отбора заказов

        :raises FinancialReporterError:

        :return: FinancialReport
        """
        self._active_orders = self._filter_orders(period)
        if not self._active_orders:
            raise FinancialReporterError("За выбранный период нет заказов")

        revenue = self._build_revenue()
        margin = self._build_margin(revenue)
        unit = self._build_unit_economics()
        orders = self._build_orders_stats()
        tax = self._build_tax_metrics(revenue)

        return FinancialReport(
            period=period,
            revenue=revenue,
            margin=margin,
            unit_economics=unit,
            orders=orders,
            tax=tax,
        )

    def get_report(self) -> FinancialReport:
        """
        build financial report for all available orders

        :raises FinancialReporterError:

        :return: FinancialReport
        """
        if not self._orders:
            raise FinancialReporterError("Список заказов пуст")

        period = self._build_period()
        return self.build(period)

    def _filter_orders(self, period: ReportPeriod) -> list[Order]:
        """
        filter orders by period

        :param period: период отчёта

        :return: list[Order]
        """

        return [
            order
            for order in self._orders
            if period.start_date <= order.creation_date.replace(tzinfo=timezone.utc) <= period.end_date
        ]

    def _build_period(self) -> ReportPeriod:
        """
        calculate report period

        :return: ReportPeriod
        """
        dates = [order.creation_date for order in self._orders]
        return ReportPeriod(
            start_date=min(dates),
            end_date=max(dates),
            label="auto",
        )

    def _build_revenue(self) -> RevenueMetrics:
        """
        calculate revenue metrics

        :return: RevenueMetrics
        """
        total_revenue = Decimal("0")
        total_cost = Decimal("0")
        total_profit = Decimal("0")

        for order in self._active_orders:
            if not order.cost_report:
                continue
            total_revenue += order.cost_report.edition_cost
            total_profit += order.cost_report.profit_after_tax
            total_cost += (
                order.cost_report.edition_cost
                - order.cost_report.profit_after_tax
            )

        count = len(self._active_orders)
        avg_check = total_revenue / count if count else Decimal("0")
        avg_profit = total_profit / count if count else Decimal("0")

        return RevenueMetrics(
            total_revenue=total_revenue,
            total_cost_price=total_cost,
            total_profit_before_tax=total_profit,
            total_profit_after_tax=total_profit,
            average_order_value=avg_check,
            average_profit_per_order=avg_profit,
        )

    def _build_margin(self, revenue: RevenueMetrics) -> MarginMetrics:
        """
        calculate margin metrics

        :param revenue: revenue metrics

        :return: MarginMetrics
        """
        gross = revenue.total_revenue - revenue.total_cost_price
        ratio = (
            gross / revenue.total_revenue
            if revenue.total_revenue
            else Decimal("0")
        )

        return MarginMetrics(
            gross_margin_ratio=ratio,
            net_margin_ratio=ratio,
            average_markup=self._average_markup(),
        )

    def _build_unit_economics(self) -> UnitEconomics:
        """
        calculate unit economics

        :return: UnitEconomics
        """
        total_units = 0
        total_cost = Decimal("0")
        total_price = Decimal("0")

        for order in self._active_orders:
            if not order.cost_report:
                continue
            total_units += order.unit_count
            total_cost += order.cost_report.unit_cost_price
            total_price += order.cost_report.unit_cost

        if total_units == 0:
            return UnitEconomics(
                average_unit_cost_price=Decimal("0"),
                average_unit_price=Decimal("0"),
                average_profit_per_unit=Decimal("0"),
            )

        avg_cost = total_cost / total_units
        avg_price = total_price / total_units

        return UnitEconomics(
            average_unit_cost_price=avg_cost,
            average_unit_price=avg_price,
            average_profit_per_unit=avg_price - avg_cost,
        )

    def _build_orders_stats(self) -> OrdersStats:
        """
        calculate orders stats

        :return: OrdersStats
        """
        profits = [
            order.cost_report.profit_after_tax
            for order in self._active_orders
            if order.cost_report
        ]

        if not profits:
            profits = [Decimal("0")]

        profitable = sum(1 for profit in profits if profit > 0)
        unprofitable = sum(1 for profit in profits if profit <= 0)

        return OrdersStats(
            total_orders=len(self._active_orders),
            profitable_orders=profitable,
            unprofitable_orders=unprofitable
        )

    def _build_tax_metrics(self, revenue: RevenueMetrics) -> TaxMetrics:
        """
        calculate tax metrics

        :param revenue: revenue metrics

        :return: TaxMetrics
        """
        tax = revenue.total_profit_before_tax - revenue.total_profit_after_tax
        rate = (
            tax / revenue.total_profit_before_tax
            if revenue.total_profit_before_tax
            else Decimal("0")
        )

        return TaxMetrics(
            total_tax=tax,
            effective_tax_rate=rate,
        )

    def _average_markup(self) -> Decimal:
        """
        calculate average markup

        :return: Decimal
        """
        values = [
            order.economy.markup
            for order in self._active_orders
        ]
        if not values:
            return Decimal("0")
        return sum(values) / len(values)