"""Prices a press sheet, a block, a product, and an order."""

from __future__ import annotations

from backend.core.accountant.money import Money
from backend.new_core.accountant.cost_report import CostReport
from backend.new_core.accountant.order_report import OrderReport
from backend.new_core.accountant.percent import Percent
from backend.new_core.order.additional_work import AdditionalWork
from backend.new_core.order.order import Order
from backend.new_core.print_run.print_run import PrintRun


TAX_COMPENSATION_FACTOR = Percent(93)


def _volume_factor(sheet_count: int) -> Percent:
    if sheet_count < 5:
        return Percent(30)
    if sheet_count < 100:
        return Percent(15)
    if sheet_count < 500:
        return Percent(5)
    return Percent(0)


class Accountant:
    """Turns runs and additional work into cost and order reports."""

    @staticmethod
    def sheet_cost_report(
            run: PrintRun,
    ) -> CostReport:
        """Returns the operation cost of one press sheet.

        Part markup and the volume markup are added after the operations.
        Each one is a percent of material, startup, and work. The second
        does not scale the first.

        :return: material and work as each operation returns them, plus
        each startup divided by the press sheet count, plus markup.
        """
        report = CostReport.zero()

        for operation in run.operations:
            report += CostReport(
                material=operation.material_price(),
                startup=operation.startup_price() / run.press_sheet_count(),
                work=operation.work_price(),
                markup=Money.zero(),
            )

        report = report.apply_markup(run.block.markup)
        report = report.apply_markup(_volume_factor(run.press_sheet_count()))

        return report

    def list_report(
            self,
            run: PrintRun,
    ) -> CostReport:
        """Returns the press-sheet cost divided across the target sheets.

        :return: the press-sheet report divided by the imposition count.
        """
        sheet_report = self.sheet_cost_report(run)
        return sheet_report / run.imposition.count()

    def block_cost_report(self, run: PrintRun) -> CostReport:
        """Returns the target-sheet cost times the block count.

        :return: the list report multiplied by the block count.
        """
        report = self.list_report(run)
        return report * run.block.count

    def product_cost_report(
            self,
            associated_runs: list[PrintRun],
            works: tuple[AdditionalWork, ...],
    ) -> CostReport:
        """Returns the sum of the block reports and the additional work.

        Additional work does not receive the volume markup.

        :param associated_runs: the runs whose blocks are priced.
        :param works: the additional work of the product. Each price is
        work, and its markup is a percent of that price.

        :return: one report. An empty run list and an empty work tuple
        yield zero.
        """
        total_report = CostReport.zero()
        for run in associated_runs:
            total_report += self.block_cost_report(run)

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
            associated_runs: list[PrintRun],
            works: tuple[AdditionalWork, ...],
            order: Order,
    ) -> CostReport:
        """Returns the product report times the order count.

        Tax compensation is not applied.

        :param associated_runs: the runs whose blocks are priced.
        :param works: the additional work of the product.
        :param order: the order whose count scales the report.

        :return: the product report multiplied by the order count.
        """
        report = self.product_cost_report(associated_runs, works)
        return report * order.count

    def order_report(
            self,
            order: Order,
            associated_runs: list[PrintRun],
    ) -> OrderReport:
        """Returns the priced order after tax compensation.

        :param order: the order whose product work and count are priced.
        :param associated_runs: the runs whose blocks are priced.

        :return: product price, order price, income, and imposition counts
        in run order. The product report is multiplied by 100/93. The order
        price is that report times the order count. Income is the order
        price minus the order cost price.
        """
        product_report = self.product_cost_report(
            associated_runs,
            order.product.operations,
        )
        product_report = product_report * TAX_COMPENSATION_FACTOR.compensation()

        order_report = product_report * order.count
        impositions = tuple(
            run.imposition.count() for run in associated_runs
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
