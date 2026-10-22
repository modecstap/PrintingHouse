from decimal import Decimal

from backend.workplace.chroma import Chroma
from backend.workplace.cost_order import PressSheet
from backend.workplace.reports import PrintingReport


class PrintingWorkplace:
    @staticmethod
    def report(
            press_sheet: PressSheet,
        chroma: Chroma,
        sheet_count: int,
    ) -> PrintingReport:
        """Возвращает отчёт одной печати.

        Предусловия: width и height — ширина и высота печатного листа
        в миллиметрах. Поля листа в метод не входят.
        density — плотность бумаги в граммах на квадратный метр.
        chroma — цветность модуля.
        sheet_count — число листов задания без приладки.
        Результат: PrintingReport. mass_kg — масса одного листа.
        На число листов и на приладку масса не умножается.
        human_operations равен 0 при ZERO_ZERO и sheet_count иначе.
        Побочные эффекты: нет. Аргументы не меняются.
        """
        area_mm2 = Decimal(press_sheet.width * press_sheet.height)
        area_m2 = area_mm2 / Decimal(1_000_000)
        mass_kg = area_m2 * (Decimal(press_sheet.density) / Decimal(1000))

        if chroma is Chroma.ZERO_ZERO:
            human_operations = 0
        else:
            human_operations = sheet_count

        used_ink = chroma.consumed_sheets(sheet_count)

        return PrintingReport(
            mass_kg=mass_kg,
            used_ink=used_ink,
            sheet_count=sheet_count,
            human_operations=human_operations,
        )
