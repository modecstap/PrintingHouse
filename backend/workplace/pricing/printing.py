from decimal import Decimal

from backend.workplace.money import Money
from backend.workplace.pricing.stage_cost import StageCost
from backend.workplace.reports import PrintingReport


def price_printing(
    report: PrintingReport,
    paper_cost: Decimal,
    ink_cost: Decimal,
    black_ink_cost: Decimal,
    printer_salary: Decimal,
) -> StageCost:
    """Считает запуск, материал и зарплату печати до наценки.

    Предусловия: ставки — Decimal. mass_kg — масса одного листа.
    При sheet_count == 0 краска равна нулю.
    Результат: StageCost. Запуск ноль.
    Материал — бумага одного листа плюс краска одного листа.
    Зарплата — ставка один раз при ненулевых human_operations и ноль иначе.
    Суммы до копейки не округляются.
    Побочные эффекты: нет.
    Ошибки: InvalidPriceException, если сумма меньше нуля.
    """
    paper = Money(paper_cost) * report.mass_kg
    ink = _ink(report, ink_cost, black_ink_cost)
    salary = Money.zero()
    if report.human_operations != 0:
        # Зарплата печатника входит в цену листа один раз, не умножается на число листов.
        salary = Money(printer_salary)
    return StageCost(
        startup_cost=Money.zero(),
        material_cost=paper + ink,
        salary=salary,
    )


def _ink(report: PrintingReport, ink_cost: Decimal, black_ink_cost: Decimal) -> Money:
    # костыль от старой реализации где на цвета была одна суммарная стоимость
    # used_ink списывает краску на все листы задания. В цену листа входит один лист.
    color_price = Money(ink_cost / 4)
    black_price = Money(black_ink_cost)
    cyan, magenta, yellow, black = report.used_ink
    total = color_price * (cyan + magenta + yellow) + black_price * black
    sheets = report.sheet_count
    if sheets == 0:
        return Money.zero()
    return total / sheets
