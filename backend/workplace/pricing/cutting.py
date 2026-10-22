from decimal import Decimal

from backend.workplace.money import Money
from backend.workplace.pricing.stage_cost import StageCost
from backend.workplace.reports import CuttingReport


def price_cutting(
    report: CuttingReport,
    cutting_cost: Decimal,
    internal_sheet_count: int,
) -> StageCost:
    """Считает запуск, материал и зарплату резки до наценки.

    Предусловия: internal_sheet_count не ноль. Деление на ноль не обрабатывается.
    Результат: запуск и материал ноль.
    Зарплата — ставка реза умножить на human_cuts и разделить на internal_sheet_count.
    Без округления до копейки.
    Побочные эффекты: нет.
    Ошибки: InvalidPriceException, если сумма меньше нуля.
    """
    salary = (Money(cutting_cost) * report.human_cuts) / internal_sheet_count
    return StageCost(
        startup_cost=Money.zero(),
        material_cost=Money.zero(),
        salary=salary,
    )
