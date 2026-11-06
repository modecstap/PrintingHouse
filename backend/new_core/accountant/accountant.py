from __future__ import annotations

from typing import TYPE_CHECKING

from backend.core.accountant.money import Money
from backend.new_core.accountant.report import CostReport
from backend.new_core.operations.run_operation import RunOperation

if TYPE_CHECKING:
    from backend.new_core.print_run.print_run import PrintRun


class Accountant:

    @staticmethod
    def sheet_cost_report(
            operations: list[RunOperation],
            sheet_count: int
    ) -> CostReport:
        """Returns the operation cost of one press sheet.

        :param operations: the operations to price. An empty list yields
        zero.
        :param sheet_count: how many press sheets share each startup.

        :return: material and work as each operation returns them, plus
        each startup divided by sheet_count.
        """
        material = Money.zero()
        startup = Money.zero()
        work = Money.zero()

        for operation in operations:
            material += operation.material_price()
            startup += operation.startup_price() / sheet_count
            work += operation.work_price()

        return CostReport(
            material=material,
            startup=startup,
            work=work,
        )

    def list_report(
            self,
            operations: list[RunOperation],
            sheet_count: int,
            items_per_sheet: int
    ) -> CostReport:
        """Returns the press-sheet cost divided across the target sheets.

        :param operations: the operations to price.
        :param sheet_count: how many press sheets share each startup.
        :param items_per_sheet: how many target sheets share one press
        sheet.

        :return: the press-sheet report divided by items_per_sheet.
        """
        sheet_report = self.sheet_cost_report(operations, sheet_count)
        return sheet_report / items_per_sheet

    def run_cost_report(self, run: PrintRun) -> CostReport:
        """Returns the operation cost of every press sheet in the run.

        :param run: the run whose operations are priced. An empty
        operation list yields zero. The block paper, the target sheet
        price, the block count, the order count, and additional work
        are not included.

        :return: the press-sheet report times the press sheet count.
        """
        sheet_report = self.sheet_cost_report(
            run.operations,
            run.press_sheet_count()
        )
        return sheet_report * run.press_sheet_count()
