from decimal import Decimal

from backend.workplace.cost_order import PressPricing
from backend.workplace.money import Money
from backend.workplace.pricing.stage_cost import StageCost
from backend.workplace.reports import PrintingReport


def price_printing(
    report: PrintingReport,
    press_pricing: PressPricing,
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
    paper = press_pricing.paper * report.mass_kg

    ink = Money.zero()
    cyan, magenta, yellow, black = report.used_ink
    total = (
            press_pricing.cyan * cyan +
            press_pricing.magenta * magenta +
            press_pricing.yellow * yellow +
            press_pricing.black * black
    )
    sheets = report.sheet_count
    if sheets != 0:
        ink = total / sheets

    salary = Money.zero()
    if report.human_operations != 0:
        salary = press_pricing.salary

    return StageCost(
        startup_cost=Money.zero(),
        material_cost=paper + ink,
        salary=salary,
    )
