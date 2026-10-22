from decimal import Decimal

from backend.workplace.money import Money
from backend.workplace.pricing.stage_cost import StageCost
from backend.workplace.reports import DieCuttingReport


def price_die_cutting(report: DieCuttingReport, die_cutting_cost: Decimal) -> StageCost:
    """Считает запуск, материал и зарплату высечки до наценки.

    Предусловия: отчёт есть. sheet_count множителем не является.
    Результат: запуск и материал ноль, зарплата равна ставке один раз.
    Без округления до копейки.
    Побочные эффекты: нет.
    Ошибки: InvalidPriceException, если сумма меньше нуля.
    """
    if not report:
        return StageCost.zero()

    if report.sheet_count == 0:
        return StageCost.zero()

    salary = Money(die_cutting_cost)
    return StageCost(
        startup_cost=Money.zero(),
        material_cost=Money.zero(),
        salary=salary,
    )
