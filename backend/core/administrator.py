import math
from collections.abc import Mapping

from backend.core.accountant.accountant import Accountant
from backend.core.order import Order
from backend.core.reports import CostReport, PrintingCase
from backend.core.sheet.sheet import Sheet
from backend.core.workplaces.cutting.cutting import CuttingWorkplace
from backend.core.workplaces.die_cutting.die_cutting import \
    DieCuttingWorkplace
from backend.core.workplaces.lamination.lamination import \
    LaminationWorkplace
from backend.core.workplaces.printing.printing import PrintingWorkplace


class Administrator:
    def __init__(self) -> None:
        """Creates the workplaces and the accountant."""
        self.printing = PrintingWorkplace()
        self.cutting = CuttingWorkplace()
        self.lamination = LaminationWorkplace()
        self.die_cutting = DieCuttingWorkplace()
        self.accountant = Accountant()

    def report_cost(
        self, order: Order, sheets: Mapping[int, Sheet]
    ) -> CostReport:
        """Calculates the order cost in memory.

        :param order:
        :param sheets: sheet id to the loaded sheet. Each printing is priced
        from the sheet named by specification.press_sheet.

        :raises ZeroDivisionError: if a cell side is zero
        or the number of items on the sheet is zero. The method does not catch it.

        :return: a CostReport. The printings in it follow the order of printings.
        Paper for one sheet is that sheet's cost multiplied by the mass of one sheet.
        """
        cases: list[PrintingCase] = []
        for printing in order.printings:
            spec = printing.specification
            sheet_id = spec.press_sheet
            if sheet_id is None:
                raise KeyError(sheet_id)
            sheet = sheets[sheet_id]
            item_count = spec.count * order.specification.unit_count
            items_per_sheet = sheet.item_count(spec.list, spec.spacing)
            cut_count = sheet.cut_needed(spec.list, spec.spacing)
            internal_sheet_count = math.ceil(
                item_count / items_per_sheet * 1.03
            )
            printing_report = self.printing.report(
                sheet=sheet,
                chroma=spec.chroma,
                sheet_count=internal_sheet_count,
            )
            cutting_report = self.cutting.report(
                internal_sheet_count=internal_sheet_count,
                stack_height=printing.stack_height,
                density=sheet.density,
                cut_count=cut_count,
            )
            lamination_report = self.lamination.report(spec.lamination)
            die_cutting_report = self.die_cutting.report(
                internal_sheet_count, spec.die_cutting
            )

            cases.append(
                PrintingCase(
                    item_count=item_count,
                    items_per_sheet=items_per_sheet,
                    internal_sheet_count=internal_sheet_count,
                    calculations=(
                        printing.press_pricing.attach(
                            printing_report, sheet.cost
                        ),
                        printing.cut_pricing.attach(
                            cutting_report, internal_sheet_count
                        ),
                        printing.lamination_pricing.attach(
                            lamination_report, internal_sheet_count
                        ),
                        printing.die_cut_pricing.attach(die_cutting_report),
                    )
                )
            )
        return self.accountant.calculate(
            cases,
            tuple(
                operation.cost
                for operation in order.specification.operations
            ),
            order.tax_rate,
            order.specification.markup,
            order.specification.unit_count,
        )
