from decimal import Decimal

from backend.core.workplaces.printing.models import PrintingReport, Chroma, \
    PressSheet


class PrintingWorkplace:
    @staticmethod
    def report(
        press_sheet: PressSheet,
        chroma: Chroma,
        sheet_count: int,
    ) -> PrintingReport:
        """Returns the report of one printing.

        :param press_sheet: width and height are the press sheet width
        and height in millimeters.
        :param chroma: the module's chroma.
        :param sheet_count: the job sheet count without fitting.

        :return: a PrintingReport. mass_kg is the mass of one sheet.
        The mass is not multiplied by the sheet count or by the fitting.
        human_operations is 0 for ZERO_ZERO and sheet_count otherwise.
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
