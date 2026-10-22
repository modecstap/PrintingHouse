from decimal import Decimal

from backend.aggregate.printer.values.chroma import Chroma
from backend.models.economy import Economy
from backend.models.operation import Operation
from backend.models.order_cost_report import OrderCostReport
from backend.models.printing_cost_report import PrintingCostReport
from backend.workplace.money import Money
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
    cost_price = Money(Decimal(0))
    cost = Money(Decimal(0))

    paper = Money(case.production.paper_cost) * case.printing.mass_kg
    cost_price = cost_price + paper
    cost = cost + paper

    ink = _ink(case)
    cost_price = cost_price + ink
    cost = cost + ink

    if case.printing.human_operations != 0:
        # Зарплата печатника входит в цену листа один раз, не умножается на число листов.
        cost = cost + Money(case.production.printer_salary)

    cost = cost + (
        Money(case.production.cutting_cost) * case.cutting.human_cuts
    ) / case.internal_sheet_count

    if case.lamination is not None:
        film = Money(case.production.lamination_cost) * case.lamination.film_sides
        startup = Money(Decimal(200)) / case.internal_sheet_count
        cost_price = cost_price + film / 2 + startup
        cost = cost + film + startup

    if case.die_cutting is not None:
        # Число листов высечки не множитель: ставка уже за один лист.
        cost = cost + Money(case.production.die_cutting_cost)

    cost = cost * (economy.markup / 100 + 1)
    cost = cost * _volume_factor(case.internal_sheet_count)
    cost = cost / economy.tax_rate
    cost = cost.quantize()
    cost_price = cost_price.quantize()

    items_on_sheet = min(case.items_per_sheet, case.item_count)
    unit_cost = (cost / items_on_sheet).quantize()
    unit_cost_price = (cost_price / items_on_sheet).quantize()
    edition_cost = (unit_cost * case.item_count).quantize()
    edition_cost_price = (unit_cost_price * case.item_count).quantize()
    # Прибыль остаётся Decimal: Money не хранит отрицательную сумму.
    profit_before_tax = edition_cost.amount - edition_cost_price.amount
    profit_after_tax = profit_before_tax * economy.tax_rate
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


def _ink(case: PrintingCase) -> Money:
    black = case.production.black_ink_cost
    color = case.production.ink_cost
    chroma = case.printing.chroma
    if chroma is Chroma.ZERO_ZERO:
        return Money(Decimal(0))
    if chroma is Chroma.ONE_ZERO:
        return Money(black)
    if chroma is Chroma.ONE_ONE:
        return Money(black) * 2
    if chroma is Chroma.FOUR_ZERO:
        return Money(color)
    if chroma is Chroma.FOUR_ONE:
        return Money(color) + Money(black)
    if chroma is Chroma.FOUR_FOUR:
        return Money(color) * 2
    return Money(Decimal(0))


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
