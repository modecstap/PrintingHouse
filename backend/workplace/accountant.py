from decimal import Decimal

from backend.models.economy import Economy
from backend.models.operation import Operation
from backend.models.order_cost_report import OrderCostReport
from backend.models.printing_cost_report import PrintingCostReport
from backend.workplace.money import Money
from backend.workplace.pricing.cutting import price_cutting
from backend.workplace.pricing.die_cutting import price_die_cutting
from backend.workplace.pricing.lamination import price_lamination
from backend.workplace.pricing.printing import price_printing
from backend.workplace.pricing.stage_cost import StageCost
from backend.workplace.reports import PrintingCase


class Accountant:
    def calculate(
        self,
        printings: list[PrintingCase],
        operations: list[Operation],
        economy: Economy,
        unit_count: int,
    ) -> OrderCostReport:
        """Собирает стоимость заказа из отчётов мест и ставок.

        Предусловия: printings — печати в порядке заказа.
        Ставки печати лежат в case.production.
        Наценка и налог лежат в economy.
        Количества берутся из PrintingCase и отчётов мест.
        Ламинация None: плёнка и запуск не входят в сумму.
        Высечка None: плата за высечку не входит в сумму.
        internal_sheet_count, tax_rate, unit_count и делитель изделия не равны нулю.
        Деление на ноль не обрабатывается.
        Результат: OrderCostReport.
        Список printing_cost_reports идёт в порядке printings.
        Пустой список операций оставляет суммы операций нулём.
        Побочные эффекты: нет. Аргументы не меняются.
        """
        printing_reports: list[PrintingCostReport] = []
        editions_cost = Money(Decimal(0))
        editions_cost_price = Money(Decimal(0))
        for case in printings:
            report = _price_printing(case, economy)
            printing_reports.append(report)
            editions_cost = editions_cost + Money(report.edition_cost)
            editions_cost_price = editions_cost_price + Money(report.edition_cost_price)

        operation_cost, operation_cost_price = _price_operations(
            operations, economy, unit_count
        )
        unit_cost_price = (
            (editions_cost_price + operation_cost_price) / unit_count
        ).quantize()
        unit_cost = ((editions_cost + operation_cost) / unit_count).quantize()
        edition_cost = unit_cost * unit_count
        # Прибыль остаётся Decimal: Money не хранит отрицательную сумму.
        profit_after_tax = edition_cost.amount - (unit_cost_price * unit_count).amount
        return OrderCostReport(
            unit_cost_price=unit_cost_price.amount,
            unit_cost=unit_cost.amount,
            edition_cost=edition_cost.amount,
            profit_after_tax=profit_after_tax,
            printing_cost_reports=printing_reports,
        )


def _price_printing(case: PrintingCase, economy: Economy) -> PrintingCostReport:
    printing = price_printing(
        case.printing,
        case.production.paper_cost,
        case.production.ink_cost,
        case.production.black_ink_cost,
        case.production.printer_salary,
    )
    cutting = price_cutting(
        case.cutting,
        case.production.cutting_cost,
        case.internal_sheet_count,
    )
    if case.lamination is None:
        lamination = StageCost.zero()
    else:
        lamination = price_lamination(
            case.lamination,
            case.production.lamination_cost,
            case.internal_sheet_count,
        )

    if case.die_cutting is None:
        die_cutting = StageCost.zero()
    else:
        die_cutting = price_die_cutting(
            case.die_cutting,
            case.production.die_cutting_cost,
        )
    startup = (
        printing.startup_cost
        + cutting.startup_cost
        + lamination.startup_cost
        + die_cutting.startup_cost
    )
    material = (
        printing.material_cost
        + cutting.material_cost
        + lamination.material_cost
        + die_cutting.material_cost
    )
    salary = printing.salary + cutting.salary + lamination.salary + die_cutting.salary

    markup = (economy.markup / 100 + 1)
    volume_factor = _volume_factor(case.internal_sheet_count)
    tax_compensation = 1/economy.tax_rate

    cost_price = (startup + material).quantize()
    cost = (
        (startup + material + salary) * markup * volume_factor * tax_compensation
    ).quantize()

    items_on_sheet = min(case.items_per_sheet, case.item_count)
    unit_cost = (cost / items_on_sheet).quantize()
    unit_cost_price = (cost_price / items_on_sheet).quantize()
    edition_cost = (unit_cost * case.item_count).quantize()
    edition_cost_price = (unit_cost_price * case.item_count).quantize()
    # Прибыль остаётся Decimal: Money не хранит отрицательную сумму.
    profit_before_tax = edition_cost.amount - edition_cost_price.amount
    profit_after_tax = profit_before_tax / tax_compensation
    return PrintingCostReport(
        items_per_sheet=case.items_per_sheet,
        sheet_count=case.sheet_count,
        unit_cost_price=unit_cost_price.amount,
        unit_cost=unit_cost.amount,
        edition_cost_price=edition_cost_price.amount,
        edition_cost=edition_cost.amount,
        profit_before_tax=profit_before_tax,
        profit_after_tax=profit_after_tax,
    )


def _volume_factor(internal_sheet_count: int) -> Decimal:
    if internal_sheet_count < 5:
        return Decimal("1.3")
    if internal_sheet_count < 100:
        return Decimal("1.15")
    if internal_sheet_count < 500:
        return Decimal("1.05")
    return Decimal("1")


def _price_operations(
    operations: list[Operation],
    economy: Economy,
    unit_count: int,
) -> tuple[Money, Money]:
    operation_cost_price = Money(Decimal(0))
    operation_cost = Money(Decimal(0))
    for operation in operations:
        operation_cost_price = operation_cost_price + Money(operation.cost) * unit_count
        total_markup = (1 + economy.markup / 100) * (1 / economy.tax_rate)
        # База цены — уже накопленная себестоимость, включая текущую операцию.
        operation_cost = operation_cost + operation_cost_price * total_markup
    return operation_cost, operation_cost_price
