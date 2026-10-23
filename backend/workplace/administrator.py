import math

from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_optimizer import (
    PlacementOptimizer,
)
from backend.models.list_size import ListSize
from backend.models.press_sheet import PressSheet
from backend.workplace.accountant import Accountant
from backend.workplace.cost_order import CostOrder
from backend.workplace.reports import CostReport, PrintingCase, PressCase, \
    LaminationCase, DieCuttingCase, CuttingCase
from backend.workplace.workplaces.cutting.cutting import CuttingWorkplace
from backend.workplace.workplaces.die_cutting.die_cutting import \
    DieCuttingWorkplace
from backend.workplace.workplaces.lamination.lamination import \
    LaminationWorkplace
from backend.workplace.workplaces.printing.printing import PrintingWorkplace


class Administrator:
    def __init__(self) -> None:
        """Создаёт рабочие места и бухгалтера.

        Побочные эффекты: запоминает печать, резку, ламинацию,
        высечку и бухгалтера. Другого состояния нет.
        """
        self.printing = PrintingWorkplace()
        self.cutting = CuttingWorkplace()
        self.lamination = LaminationWorkplace()
        self.die_cutting = DieCuttingWorkplace()
        self.accountant = Accountant()

    def report_cost(self, order: CostOrder) -> CostReport:
        """Считает стоимость заказа в памяти.

        Предусловие: данные, которые fit_order считает без деления на ноль.
        Результат: CostReport. Печати в нём идут в порядке printings.
        Аргумент не меняется.
        Деление на ноль не обрабатывается.
        """
        cases: list[PrintingCase] = []
        for printing in order.printings:
            item_count = printing.count * order.unit_count
            placement = PlacementOptimizer(
                press_sheet=PressSheet(
                    width=printing.press_sheet.width,
                    height=printing.press_sheet.height,
                    spacing=printing.press_sheet.spacing,
                ),
                list_size=ListSize(
                    width=printing.list.width,
                    height=printing.list.height,
                    bleeds=printing.list.bleeds,
                ),
            ).get_best_solution()
            items_per_sheet = placement.get_items_count()
            cut_count = placement.get_cut_count()
            sheet_count = math.ceil(item_count / items_per_sheet)
            # Приладка внутри суммы до ceil: sheet_count плюс приладка
            # после округления даёт другое внутреннее число листов.
            internal_sheet_count = math.ceil(
                item_count / items_per_sheet + printing.sheet_by_fitting
            )
            printing_report = self.printing.report(
                press_sheet=printing.press_sheet,
                chroma=printing.chroma,
                sheet_count=sheet_count,
            )
            cutting_report = self.cutting.report(
                internal_sheet_count=internal_sheet_count,
                stack_height=printing.stack_height,
                density=printing.press_sheet.density,
                cut_count=cut_count,
            )
            lamination_report = self.lamination.report(printing.lamination)
            die_cutting_report = self.die_cutting.report(sheet_count, printing.die_cutting)

            cases.append(
                PrintingCase(
                    item_count=item_count,
                    items_per_sheet=items_per_sheet,
                    sheet_count=sheet_count,
                    internal_sheet_count=internal_sheet_count,
                    press=PressCase(
                        printing=printing_report,
                        press_pricing=printing.press_pricing,
                    ),
                    cutting=CuttingCase(
                        cutting=cutting_report,
                        cut_pricing=printing.cut_pricing,
                    ),
                    lamination=LaminationCase(
                        lamination=lamination_report,
                        lamination_pricing=printing.lamination_pricing,
                    ),
                    die_cutting=DieCuttingCase(
                        die_cutting=die_cutting_report, 
                        die_cut_pricing=printing.die_cut_pricing,
                    ),
                )
            )
        return self.accountant.calculate(
            cases,
            order.operation_costs,
            order.tax_rate,
            order.markup,
            order.unit_count,
        )
