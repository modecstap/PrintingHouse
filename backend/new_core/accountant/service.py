from backend.core.accountant.money import Money
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.print_run.report import CostReport


class Accountant:
    def run_cost_report(self, run: PrintRun) -> CostReport:
        """Returns the eight money fields of the run.

        :param run: the run whose operations come from operations(). An
        empty sequence yields zero in every field. The block paper, the
        target sheet price, the block count, the order count, and
        additional work are not included.

        :return: the press-sheet material, startup, work, and their sum,
        plus those three parts divided by the smaller of the grid count
        and the required count. The target total is the sum of the three
        target parts.
        """
        items_per_sheet = run.imposition.count()

        material = Money.zero()
        startup = Money.zero()
        work = Money.zero()
        for operation in run.operations():
            material += operation.material_price()
            startup += operation.startup_price()
            work += operation.work_price()

        press_sheet_total = material + startup + work
        divisor = min(items_per_sheet, run.required_count)
        target_material = material / divisor
        target_startup = startup / divisor
        target_work = work / divisor
        return CostReport(
            target_material=target_material,
            target_startup=target_startup,
            target_work=target_work,
            target_total=target_material + target_startup + target_work,
            press_sheet_material=material,
            press_sheet_startup=startup,
            press_sheet_work=work,
            press_sheet_total=press_sheet_total,
        )
