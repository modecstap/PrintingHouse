import math

from backend.workplace.reports import CuttingReport


class CuttingWorkplace:
    def report(
        self,
        internal_sheet_count: int,
        stack_height: int,
        density: int,
        cut_count: int,
    ) -> CuttingReport:
        """Возвращает число резов человека для одной печати.

        Предусловия: internal_sheet_count — внутреннее число листов
        с приладкой. stack_height — высота стопки резака.
        density — плотность бумаги в граммах на квадратный метр.
        cut_count — число резов раскладки.
        Ставка реза в метод не входит.
        Результат: CuttingReport. human_cuts — число резов человека.
        Плата за резы на число листов не делится.
        Деление на ноль не обрабатывается.
        Побочные эффекты: нет. Аргументы не меняются.
        """
        sheet_in_stack = max(math.ceil(stack_height * 1200 / density), 0)
        human_cuts = math.ceil(internal_sheet_count / sheet_in_stack) * cut_count
        return CuttingReport(human_cuts=human_cuts)
