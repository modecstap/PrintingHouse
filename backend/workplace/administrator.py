import math

from backend.workplace.accountant.accountant import Accountant
from backend.workplace.cost_order import Order
from backend.workplace.placement import place_on_sheet
from backend.workplace.reports import CostReport, PrintingCase
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

    def report_cost(self, order: Order) -> CostReport:
        """Считает стоимость заказа в памяти.

        Предусловие: нет.
        Результат: CostReport. Печати в нём идут в порядке printings.
        Аргумент не меняется.
        Нулевая сторона клетки и ноль изделий на листе поднимают
        ZeroDivisionError. Метод это не ловит.
        """
        cases: list[PrintingCase] = []
        for printing in order.printings:
            item_count = printing.count * order.unit_count
            placement = place_on_sheet(printing.press_sheet, printing.list)
            items_per_sheet = placement.items_per_sheet
            cut_count = placement.cut_count
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
                    calculations=(
                        printing.press_pricing.attach(printing_report),
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
            tuple(operation.cost for operation in order.operations),
            order.tax_rate,
            order.markup,
            order.unit_count,
        )
