from backend.models.order import Order
from backend.models.order_cost_report import OrderCostReport
from backend.models.printing import Printing
from backend.models.printing_cost_report import PrintingCostReport
from backend.workplace.administrator import Administrator
from backend.workplace.chroma import Chroma
from backend.workplace.cost_order import CostOrder, CostPrinting
from backend.workplace.lamination import Lamination
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
    return CostPrinting(
        count=edition.count,
        density=edition.density,
        chroma=Chroma[edition.chroma.name],
        lamination=Lamination[edition.lamination.name],
        die_cutting=edition.die_cutting,
        sheet_by_fitting=production.sheet_by_fitting,
        stack_height=production.cutter.stack_height,
        press_sheet_width=production.press_sheet.width,
        press_sheet_height=production.press_sheet.height,
        press_sheet_spacing=production.press_sheet.spacing,
        list_width=edition.list_size.width,
        list_height=edition.list_size.height,
        list_bleeds=edition.list_size.bleeds,
        paper_cost=production.paper_cost,
        ink_cost=production.ink_cost,
        black_ink_cost=production.black_ink_cost,
        printer_salary=production.printer_salary,
        cutting_cost=production.cutting_cost,
        lamination_cost=production.lamination_cost,
        die_cutting_cost=production.die_cutting_cost,
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
