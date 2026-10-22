import math

from backend.aggregate.laminator.values.lamination import Lamination
from backend.aggregate.printer.values.chroma import Chroma
from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_optimizer import (
    PlacementOptimizer,
)
from backend.models.order import Order
from backend.models.order_cost_report import OrderCostReport
from backend.workplace.accountant import Accountant
from backend.workplace.cutting import CuttingWorkplace
from backend.workplace.die_cutting import DieCuttingWorkplace
from backend.workplace.lamination import LaminationWorkplace
from backend.workplace.printing import PrintingWorkplace
from backend.workplace.reports import PrintingCase


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

    def report_cost(self, order: Order) -> OrderCostReport:
        """Считает стоимость заказа в памяти.

        Предусловие: заказ, который fit_order считает без деления на ноль.
        Результат: OrderCostReport.
        Заказ не меняется.
        Деление на ноль не обрабатывается.
        """
        cases: list[PrintingCase] = []
        for printing in order.printings:
            item_count = printing.edition.count * order.unit_count
            placement = PlacementOptimizer(
                press_sheet=printing.production.press_sheet,
                list_size=printing.edition.list_size,
            ).get_best_solution()
            items_per_sheet = placement.get_items_count()
            cut_count = placement.get_cut_count()
            sheet_count = math.ceil(item_count / items_per_sheet)
            # Приладка внутри суммы до ceil: sheet_count плюс приладка
            # после округления даёт другое внутреннее число листов.
            internal_sheet_count = math.ceil(
                item_count / items_per_sheet + printing.production.sheet_by_fitting
            )
            printing_report = self.printing.report(
                press_sheet=printing.production.press_sheet,
                density=printing.edition.density,
                chroma=Chroma[printing.edition.chroma.name],
                sheet_count=sheet_count,
            )
            cutting_report = self.cutting.report(
                internal_sheet_count=internal_sheet_count,
                stack_height=printing.production.cutter.stack_height,
                density=printing.edition.density,
                cut_count=cut_count,
            )
            lamination = Lamination[printing.edition.lamination.name]
            lamination_report = self.lamination.report(lamination)

            die_cutting = printing.edition.die_cutting
            die_cutting_report = self.die_cutting.report(sheet_count, die_cutting)

            cases.append(
                PrintingCase(
                    item_count=item_count,
                    items_per_sheet=items_per_sheet,
                    sheet_count=sheet_count,
                    internal_sheet_count=internal_sheet_count,
                    printing=printing_report,
                    cutting=cutting_report,
                    lamination=lamination_report,
                    die_cutting=die_cutting_report,
                    production=printing.production,
                )
            )
        return self.accountant.calculate(
            cases,
            order.operations,
            order.economy,
            order.unit_count,
        )


def report_cost(order: Order) -> OrderCostReport:
    """Считает стоимость заказа в памяти.

    Предусловие: заказ, который fit_order считает без деления на ноль.
    Результат: OrderCostReport.
    Заказ не меняется.
    Деление на ноль не обрабатывается.
    """
    return Administrator().report_cost(order)
