from decimal import Decimal

from backend.core.sheet import Sheet
from backend.core.workplaces.printing.models import PrintingReport, Chroma


class PrintingWorkplace:
    @staticmethod
    def report(
        sheet: Sheet,
        chroma: Chroma,
        sheet_count: int,
    ) -> PrintingReport:
        """Returns the report of one printing.

        :param sheet: the press sheet
        :param chroma: the module's chroma.
        :param sheet_count: the job sheet count without fitting.

        :return: a PrintingReport. mass_kg is the mass of one sheet.
        The area in mm² is divided by 1_000_000 and multiplied by density / 1000.
        The mass is not multiplied by the sheet count or by the fitting.
        human_operations is 0 for ZERO_ZERO and sheet_count otherwise.
        """
        mass_kg = Decimal(sheet.mass())

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
