from backend.workplace.accountant.money import Money
from backend.workplace.accountant.pricing.calculatable import Calculatable
from backend.workplace.accountant.pricing.stage_cost import StageCost
from backend.workplace.workplaces.die_cutting.models import DieCuttingReport


class DieCuttingCalculation(Calculatable):
    def __init__(self, salary: Money):
        """Запоминает ставку зарплаты высечки.

        Побочные эффекты: отчёт ещё не прикреплён.
        """
        self._report = None
        self._salary = salary

    def attach(self, report: DieCuttingReport) -> "DieCuttingCalculation":
        """Прикрепляет отчёт высечки.

        Предусловия: отчёт ещё не прикреплён.
        Результат: этот же объект.
        Побочные эффекты: запоминает отчёт.
        Ошибки: RuntimeError с текстом Report is already attached,
        если отчёт уже прикреплён.
        """
        if self._report is not None:
            raise RuntimeError("Report is already attached")

        self._report = report
        return self

    def calculate(self) -> StageCost:
        """Считает запуск, материал и зарплату высечки до наценки.

        Предусловия: отчёт прикреплён. sheet_count множителем не является.
        Результат: при sheet_count 0 — StageCost.zero().
        Иначе запуск и материал — ноль, зарплата равна ставке один раз.
        Без округления до копейки.
        Побочные эффекты: нет.
        Ошибки: RuntimeError с текстом Report is not attach, если отчёт
        не прикреплён. InvalidPriceException, если сумма меньше нуля.
        """
        if not self._report:
            raise RuntimeError("Report is not attach")

        if self._report.sheet_count == 0:
            return StageCost.zero()

        return StageCost(
            startup_cost=Money.zero(),
            material_cost=Money.zero(),
            salary=self._salary,
        )
