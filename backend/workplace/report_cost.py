from decimal import Decimal

from backend.models.order import Order
from backend.models.order_cost_report import OrderCostReport
from backend.models.printing import Printing
from backend.models.printing_cost_report import PrintingCostReport
from backend.workplace.administrator import Administrator
from backend.workplace.chroma import Chroma
from backend.workplace.cost_order import CostOrder, CostPrinting, PressSheet, \
    List, PressPricing, CutPricing, LaminationPricing, DieCutPricing
from backend.workplace.lamination import Lamination
from backend.workplace.money import Money
from backend.workplace.reports import CostReport


def report_cost(order: Order) -> OrderCostReport:
    """Считает стоимость заказа в памяти.

    Предусловие: заказ, который fit_order считает без деления на ноль.
    Результат: OrderCostReport.
    Заказ не меняется.
    Деление на ноль не обрабатывается.
    """
    return _saved_report(Administrator().report_cost(_cost_order(order)))


def _cost_order(order: Order) -> CostOrder:
    return CostOrder(
        unit_count=order.unit_count,
        tax_rate=order.economy.tax_rate,
        markup=order.economy.markup,
        operation_costs=tuple(operation.cost for operation in order.operations),
        printings=tuple(_cost_printing(printing) for printing in order.printings),
    )


def _cost_printing(printing: Printing) -> CostPrinting:
    edition = printing.edition
    production = printing.production
    lamination = Lamination[edition.lamination.name]
    film_rate = production.lamination_cost / 2
    return CostPrinting(
        count=edition.count,
        chroma=Chroma[edition.chroma.name],
        lamination=lamination,
        die_cutting=edition.die_cutting,
        sheet_by_fitting=production.sheet_by_fitting,
        stack_height=production.cutter.stack_height,
        press_sheet=PressSheet(
            density=edition.density,
            width=production.press_sheet.width,
            height=production.press_sheet.height,
            spacing=production.press_sheet.spacing,
        ),
        list=List(
            width=edition.list_size.width,
            height=edition.list_size.height,
            bleeds=edition.list_size.bleeds,
        ),
        press_pricing=PressPricing(
            cyan=Money(production.ink_cost/4),
            magenta=Money(production.ink_cost/4),
            yellow=Money(production.ink_cost/4),
            black=Money(production.black_ink_cost),
            paper=Money(production.paper_cost),
            salary=Money(production.printer_salary),
        ),
        cut_pricing=CutPricing(
            salary=Money(production.cutting_cost),
        ),
        lamination_pricing=LaminationPricing(
            startup=Money(Decimal("200")),
            film_cost=Money(film_rate),
            salary=Money(film_rate * lamination.film_sides()),
        ),
        die_cut_pricing=DieCutPricing(
            salary=Money(production.die_cutting_cost),
        ),
    )


def _saved_report(report: CostReport) -> OrderCostReport:
    return OrderCostReport(
        unit_cost_price=report.unit_cost_price,
        unit_cost=report.unit_cost,
        edition_cost=report.edition_cost,
        profit_after_tax=report.profit_after_tax,
        printing_cost_reports=[
            PrintingCostReport(
                items_per_sheet=printing.items_per_sheet,
                sheet_count=printing.sheet_count,
                unit_cost_price=printing.unit_cost_price,
                unit_cost=printing.unit_cost,
                edition_cost_price=printing.edition_cost_price,
                edition_cost=printing.edition_cost,
                profit_before_tax=printing.profit_before_tax,
                profit_after_tax=printing.profit_after_tax,
            )
            for printing in report.printing_cost_reports
        ],
    )
