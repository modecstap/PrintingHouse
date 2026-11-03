from decimal import Decimal

from backend.core.workplaces.printing.models import PrintingReport, Chroma


class PrintingWorkplace:
    @staticmethod
    def report(
        width: int,
        height: int,
        density: int,
        chroma: Chroma,
        sheet_count: int,
    ) -> PrintingReport:
        """Returns the report of one printing.

        :param width: the sheet width in millimeters.
        :param height: the sheet height in millimeters.
        :param density: the sheet density.
        :param chroma: the module's chroma.
        :param sheet_count: the job sheet count without fitting.

        :return: a PrintingReport. mass_kg is the mass of one sheet.
        The area in mm² is divided by 1_000_000 and multiplied by density / 1000.
        The mass is not multiplied by the sheet count or by the fitting.
        human_operations is 0 for ZERO_ZERO and sheet_count otherwise.
        """
        area_mm2 = Decimal(width * height)
        area_m2 = area_mm2 / Decimal(1_000_000)
        mass_kg = area_m2 * (Decimal(density) / Decimal(1000))

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
