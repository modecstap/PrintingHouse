from backend.workplace.accountant.money import Money
from backend.workplace.accountant.pricing.calculatable import Calculatable
from backend.workplace.accountant.pricing.stage_cost import StageCost
from backend.workplace.workplaces.lamination.models import LaminationReport


class LaminationCalculation(Calculatable):
    def __init__(self, startup: Money, film_cost: Money, salary: Money):
        """Запоминает ставки запуска, плёнки и зарплаты.

        Побочные эффекты: отчёт ещё не прикреплён.
        """
        self._report = None
        self._startup = startup
        self._film_cost = film_cost
        self._salary = salary

    def attach(
        self, report: LaminationReport, internal_sheet_count: int
    ) -> "LaminationCalculation":
        """Прикрепляет отчёт ламинации и внутреннее число листов.

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
        """Считает запуск, материал и зарплату ламинации до наценки.

        Предусловия: отчёт прикреплён. При film_sides не ноль
        internal_sheet_count не ноль. Деление на ноль не обрабатывается.
        Результат: при film_sides 0 — StageCost.zero(), и
        internal_sheet_count в этой ветке не читается, даже если ставка
        запуска задана. Иначе запуск — ставка startup, делённая на
        internal_sheet_count. Материал — film_cost умножить на film_sides.
        Зарплата равна ставке salary и на film_sides повторно не умножается.
        Запуск берётся из ставки, без отдельного числа в расчёте.
        Без округления до копейки.
        Побочные эффекты: нет.
        Ошибки: RuntimeError с текстом Report is not attach, если отчёт
        не прикреплён. InvalidPriceException, если сумма меньше нуля.
        """
        if not self._report:
            raise RuntimeError("Report is not attach")

        if self._report.film_sides == 0:
            return StageCost.zero()

        return StageCost(
            startup_cost=self._startup / self._internal_sheet_count,
            material_cost=self._film_cost * self._report.film_sides,
            salary=self._salary,
        )
