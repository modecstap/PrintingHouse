"""Prices a press target, a block, a product, and an order."""

from __future__ import annotations

from collections.abc import Sequence

from backend.new_core.accountant.run_estimate import RunEstimate
from backend.new_core.values.money import Money
from backend.new_core.accountant.cost_report import CostReport
from backend.new_core.accountant.order_report import OrderReport
from backend.new_core.values.percent import Percent
from backend.new_core.order.additional_work import AdditionalWork
from backend.new_core.order.order import Order


__all__ = [
    "TAX_COMPENSATION_FACTOR",
    "Accountant",
]

TAX_COMPENSATION_FACTOR = Percent(93)


class Accountant:
    """Turns runs and additional work into cost and order reports."""


    def product_cost_report(
            self,
            estimates: Sequence[RunEstimate],
            works: tuple[AdditionalWork, ...],
    ) -> CostReport:
        """Returns the sum of the block reports and the additional work.

        :param works: the additional work of the product. Each price is
        :param estimates: the estimates.

        :return: the CostReport result.
        """
        total_report = CostReport.zero()
        for estimate in estimates:
            total_report += estimate.block_report()

        for work in works:
            priced = CostReport(
                material=Money.zero(),
                startup=Money.zero(),
                work=work.price,
                markup=Money.zero(),
            )
            total_report += priced.apply_markup(work.markup)
        return total_report

    def order_cost_report(
            self,
            estimates: Sequence[RunEstimate],
            works: tuple[AdditionalWork, ...],
            order: Order,
    ) -> CostReport:
        """Returns the product report times the order count.

        :param works: the additional work of the product.
        :param order: the order whose count scales the report.
        :param estimates: the estimates.

        :return: the CostReport result.
        """
        report = self.product_cost_report(estimates, works)
        return report * order.count

    def order_report(
            self,
            order: Order,
            estimates: Sequence[RunEstimate],
    ) -> OrderReport:
        """Returns the priced order after tax compensation.

        :param order: the order whose product work and count are priced.
        :param estimates: the estimates.

        :return: the OrderReport result.
        """
        product_report = self.product_cost_report(
            estimates,
            order.product.operations,
        )
        product_report = product_report * TAX_COMPENSATION_FACTOR.compensation()

        order_report = product_report * order.count
        impositions = tuple(
            estimate.targets_on_imposition() for estimate in estimates
        )
        income = Money(
            order_report.total().amount - order_report.cost_price().amount
        )

        return OrderReport(
            product_price=product_report.total(),
            order_price=order_report.total(),
            income=income,
            impositions=impositions,
        )
