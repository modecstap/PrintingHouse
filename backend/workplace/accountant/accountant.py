from decimal import Decimal

from backend.workplace.accountant.money import Money
from backend.workplace.reports import CostReport, PrintingCase, PrintingCost


class Accountant:
    def calculate(
        self,
        printings: list[PrintingCase],
        operation_costs: tuple[Decimal, ...],
        tax_rate: Decimal,
        markup: Decimal,
        unit_count: int,
    ) -> CostReport:
        """Собирает стоимость заказа из отчётов мест и ставок.

        Предусловия: printings — печати в порядке заказа.
        В PrintingCase лежат четыре расчёта: печать, рез, ламинация и высечка. Отчёт каждого уже прикреплён.
        Наценка и налог переданы аргументами.
        Стоимости операций — Decimal в исходном порядке, без имени и описания.
        Количества берутся из PrintingCase и отчётов мест.
        internal_sheet_count, tax_rate, unit_count и делитель изделия не равны нулю.
        Деление на ноль не обрабатывается.
        Результат: CostReport.
        printing_cost_reports идёт в порядке printings.
        Пустой набор операций оставляет суммы операций нулём.
        Побочные эффекты: нет. Аргументы не меняются.
        """
        printing_reports: list[PrintingCost] = []
        editions_cost = Money(Decimal(0))
        editions_cost_price = Money(Decimal(0))
        for case in printings:
            report = _price_printing(case, tax_rate, markup)
            printing_reports.append(report)
            editions_cost = editions_cost + Money(report.edition_cost)
            editions_cost_price = editions_cost_price + Money(report.edition_cost_price)

        operation_cost, operation_cost_price = _price_operations(
            operation_costs, tax_rate, markup, unit_count
        )
        unit_cost_price = (
            (editions_cost_price + operation_cost_price) / unit_count
        ).quantize()
        unit_cost = ((editions_cost + operation_cost) / unit_count).quantize()
        edition_cost = unit_cost * unit_count
        # Прибыль остаётся Decimal: Money не хранит отрицательную сумму.
        profit_after_tax = edition_cost.amount - (unit_cost_price * unit_count).amount
        return CostReport(
            unit_cost_price=unit_cost_price.amount,
            unit_cost=unit_cost.amount,
            edition_cost=edition_cost.amount,
            profit_after_tax=profit_after_tax,
            printing_cost_reports=tuple(printing_reports),
        )


def _price_printing(case: PrintingCase, tax_rate: Decimal, markup: Decimal) -> PrintingCost:
    prices = [calculation.calculate() for calculation in case.calculations]

    startup = sum([price.startup_cost for price in prices], start=Money.zero())
    material = sum([price.material_cost for price in prices], start=Money.zero())
    salary = sum([price.salary for price in prices], start=Money.zero())

    markup = (markup / 100 + 1)
    volume_factor = _volume_factor(case.internal_sheet_count)
    tax_compensation = 1/tax_rate

    cost_price = (startup + material).quantize()
    cost = (
            (startup + material + salary) *
            markup * volume_factor * tax_compensation
    ).quantize()

    items_on_sheet = min(case.items_per_sheet, case.item_count)
    unit_cost = (cost / items_on_sheet).quantize()
    unit_cost_price = (cost_price / items_on_sheet).quantize()
    edition_cost = (unit_cost * case.item_count).quantize()
    edition_cost_price = (unit_cost_price * case.item_count).quantize()
    # Прибыль остаётся Decimal: Money не хранит отрицательную сумму.
    profit_before_tax = edition_cost.amount - edition_cost_price.amount
    profit_after_tax = (profit_before_tax / tax_compensation).quantize(Decimal("0.0001"))
    return PrintingCost(
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
    operation_costs: tuple[Decimal, ...],
    tax_rate: Decimal,
    markup: Decimal,
    unit_count: int,
) -> tuple[Money, Money]:
    operation_cost_price = Money(Decimal(0))
    operation_cost = Money(Decimal(0))
    for cost in operation_costs:
        operation_cost_price = operation_cost_price + Money(cost) * unit_count
        total_markup = (1 + markup / 100) * (1 / tax_rate)
        # База цены — уже накопленная себестоимость, включая текущую операцию.
        operation_cost = operation_cost + operation_cost_price * total_markup
    return operation_cost, operation_cost_price
