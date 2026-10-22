from decimal import Decimal

from backend.aggregate.printer.values.chroma import Chroma
from backend.models.press_sheet import PressSheet
from backend.workplace.reports import PrintingReport


class PrintingWorkplace:
    def report(
        self,
        press_sheet: PressSheet,
        density: int,
        chroma: Chroma,
        sheet_count: int,
    ) -> PrintingReport:
        """Возвращает отчёт одной печати.

        Предусловия: ширина и высота press_sheet в миллиметрах.
        density — плотность бумаги в граммах на квадратный метр.
        chroma — цветность принтера.
        sheet_count — число листов задания без приладки.
        Результат: PrintingReport. mass_kg — масса одного листа.
        На число листов и на приладку масса не умножается.
        human_operations равен 0 при цветности ZERO_ZERO.
        При остальных цветностях human_operations равен sheet_count.
        Побочные эффекты: нет. Аргументы не меняются.
        """
        area_m2 = Decimal(press_sheet.width * press_sheet.height) / Decimal(1_000_000)
        mass_kg = area_m2 * (Decimal(density) / Decimal(1000))
        if chroma is Chroma.ZERO_ZERO:
            human_operations = 0
        else:
            human_operations = sheet_count
        return PrintingReport(
            mass_kg=mass_kg,
            chroma=chroma,
            sheet_count=sheet_count,
            human_operations=human_operations,
        )
