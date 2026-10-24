from backend.workplace.accountant.money import Money
from backend.workplace.accountant.pricing.calculatable import Calculatable
from backend.workplace.accountant.pricing.stage_cost import StageCost
from backend.workplace.workplaces.cutting.models import CuttingReport


class CuttingCalculation(Calculatable):
    def __init__(self, salary: Money):
        """Запоминает ставку зарплаты реза.

        Побочные эффекты: отчёт ещё не прикреплён.
        """
        self._report = None
        self._salary = salary

    @property
    def salary(self) -> Money:
        """Возвращает ставку salary, переданную в конструктор."""
        return self._salary

    def attach(
        self, report: CuttingReport, internal_sheet_count: int
    ) -> "CuttingCalculation":
        """Прикрепляет отчёт реза и внутреннее число листов.

        Предусловия: отчёт ещё не прикреплён.
        Результат: этот же объект.
        Побочные эффекты: запоминает отчёт и internal_sheet_count.
        Ошибки: RuntimeError с текстом Report is already attached,
        если отчёт уже прикреплён.
        """
        if self._report is not None:
            raise RuntimeError("Report is already attached")

        self._report = report
        self._internal_sheet_count = internal_sheet_count
        return self

    def calculate(self) -> StageCost:
        """Считает запуск, материал и зарплату реза до наценки.

        Предусловия: отчёт прикреплён. internal_sheet_count не ноль.
        Деление на ноль не обрабатывается.
        Результат: запуск и материал — ноль.
        Зарплата — ставка умножить на human_cuts и разделить
        на internal_sheet_count.
        Ноль резов даёт нулевую зарплату умножением, без отдельной ветки.
        Без округления до копейки.
        Побочные эффекты: нет.
        Ошибки: RuntimeError с текстом Report is not attach, если отчёт
        не прикреплён. InvalidPriceException, если сумма меньше нуля.
        """
        if not self._report:
            raise RuntimeError("Report is not attach")

        salary = (self._salary * self._report.human_cuts) / self._internal_sheet_count
        return StageCost(
            startup_cost=Money.zero(),
            material_cost=Money.zero(),
            salary=salary,
        )
