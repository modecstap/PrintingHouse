from decimal import Decimal

from backend.workplace.cost_order import LaminationPricing
from backend.workplace.money import Money
from backend.workplace.pricing.stage_cost import StageCost
from backend.workplace.workplaces.lamination.models import LaminationReport


def price_lamination(
    report: LaminationReport,
    pricing: LaminationPricing,
    internal_sheet_count: int,
) -> StageCost:
    """Считает запуск, материал и зарплату ламинации до наценки.

    Предусловия: отчёт есть. internal_sheet_count не ноль.
    Деление на ноль не обрабатывается. 200 — запуск плёнки, не поле ставки.
    Результат: запуск 200 / internal_sheet_count.
    Стоимость плёнки — ставка умножить на film_sides.
    Материал и зарплата — по половине этой стоимости.
    Без округления до копейки.
    Побочные эффекты: нет.
    Ошибки: InvalidPriceException, если сумма меньше нуля.
    """
    if not report:
        return StageCost.zero()

    if report.film_sides == 0:
        return StageCost.zero()

    startup_cost = Money(Decimal(200)) / internal_sheet_count
    material_cost = pricing.film_cost * report.film_sides
    salary = pricing.salary

    return StageCost(
        startup_cost=startup_cost,
        material_cost=material_cost,
        salary=salary,
    )
