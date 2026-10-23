from backend.workplace.cost_order import CutPricing
from backend.workplace.money import Money
from backend.workplace.pricing.stage_cost import StageCost
from backend.workplace.workplaces.cutting.models import CuttingReport


def price_cutting(
    report: CuttingReport,
    pricing: CutPricing,
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
    salary = (pricing.salary * report.human_cuts) / internal_sheet_count
    return StageCost(
        startup_cost=Money.zero(),
        material_cost=Money.zero(),
        salary=salary,
    )
