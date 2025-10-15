from backend.instruction_maker.steps.column import Column
from backend.instruction_maker.steps.information_string import InformationString
from backend.models import Chroma, Lamination, PressSheet, ListSize


class ColumnFactory:

    @classmethod
    def create_print_information(
            cls,
            density: int,
            press_sheet: PressSheet,
            chroma: Chroma,
            lamination: Lamination,
            die_cutting: bool
    ) -> Column:
        die_cutting_format = "Да" if die_cutting else "Нет"

        if chroma == Chroma.ONE_ZERO:
            chroma_name = "1+0"
        elif chroma == Chroma.ONE_ONE:
            chroma_name = "1+1"
        elif chroma == Chroma.FOUR_ZERO:
            chroma_name = "4+0"
        elif chroma == Chroma.FOUR_ONE:
            chroma_name = "4+1"
        elif chroma == Chroma.FOUR_FOUR:
            chroma_name = "4+4"
        else:
            chroma_name = "ОШИБКА"

        if lamination == Lamination.DONT:
            lamination_name = "Нет"
        elif lamination == Lamination.ONE_ZERO:
            lamination_name = "1x0"
        elif lamination == Lamination.ONE_ONE:
            lamination_name = "1x1"
        else:
            lamination_name = "ОШИБКА"

        data = [
            InformationString(label="плотность", value=str(density), measurement="гр"),
            InformationString(label="формат бумаги", value=f"{press_sheet.width}x{press_sheet.height}",
                              measurement="мм"),
            InformationString(label="цветность", value=chroma_name, measurement=""),
            InformationString(label="ламинация", value=lamination_name, measurement=""),
            InformationString(label="высечка", value=die_cutting_format, measurement=""),
        ]
        return Column(data=data)

    @classmethod
    def create_edition_information(
            cls,
            sheet_count: int,
            fitting_count: int,
            edition_count: int,
            list_size: ListSize,
            product_per_sheet: int
    ) -> Column:
        data = [
            InformationString(label="тираж", value=f"{edition_count}", measurement="шт."),
            InformationString(label="изделий на 1 листе", value=f"{product_per_sheet}", measurement="шт."),
            InformationString(label="формат изделия", value=f"{list_size.width}x{list_size.height}", measurement="мм"),
            InformationString(label="печатных листов", value=f"{sheet_count}+{fitting_count}", measurement="шт."),
        ]
        return Column(data=data)
