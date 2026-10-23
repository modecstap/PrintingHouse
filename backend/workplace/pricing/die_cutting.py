from backend.workplace.cost_order import DieCutPricing
from backend.workplace.money import Money
from backend.workplace.pricing.stage_cost import StageCost
from backend.workplace.workplaces.die_cutting.models import DieCuttingReport


def price_die_cutting(report: DieCuttingReport, pricing: DieCutPricing) -> StageCost:
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

    return StageCost(
        startup_cost=Money.zero(),
        material_cost=Money.zero(),
        salary=pricing.salary,
    )
