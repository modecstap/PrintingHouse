from __future__ import annotations

from typing import TYPE_CHECKING

from backend.core.accountant.money import Money
from backend.new_core.accountant.report import CostReport
from backend.new_core.print_run.run_operation import RunOperation

if TYPE_CHECKING:
    from backend.new_core.print_run.print_run import PrintRun


class Accountant:

    @staticmethod
    def sheet_cost_report(operations: list[RunOperation]) -> CostReport:
        material = Money.zero()
        startup = Money.zero()
        work = Money.zero()

        for operation in operations:
            material += operation.material_price()
            startup += operation.startup_price()
            work += operation.work_price()

        return CostReport(
            material=material,
            startup=startup,
            work=work,
        )

    def list_report(
            self,
            operations: list[RunOperation],
            items_per_sheet: int
    ) -> CostReport:
        sheet_report = self.sheet_cost_report(operations)
        return sheet_report / items_per_sheet

    def run_cost_report(self, run: PrintRun) -> CostReport:
        """Returns the operation cost of every press sheet in the run.

        :param run: the run whose operations are priced. An empty
        operation list yields zero. The block paper, the target sheet
        price, the block count, the order count, and additional work
        are not included.

        :return: the press-sheet report times the press sheet count.
        """
        sheet_report = self.sheet_cost_report(run.operations)
        return sheet_report * run.press_sheet_count()
