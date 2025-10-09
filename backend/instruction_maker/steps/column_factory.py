from backend.instruction_maker.steps.column import Column
from backend.instruction_maker.steps.information_string import InformationString
from backend.models import Chroma, Lamination


class ColumnFactory:

    @classmethod
    def create_print_information(
            cls,
            density: int,
            chroma: Chroma,
            lamination: Lamination,
            die_cutting: bool
    ) -> Column:
        die_cutting_format = "Да" if die_cutting else "Нет"

        data = [
            InformationString(label="плотность", value=str(density), measurement="гр."),
            InformationString(label="цветность", value=chroma.name, measurement=""),
            InformationString(label="ламинация", value=lamination.name, measurement=""),
            InformationString(label="высечка", value=die_cutting_format, measurement=""),
        ]
        return Column(data=data)

    @classmethod
    def create_edition_information(
            cls,
            sheet_count: int,
            fitting_count: int
    ) -> Column:
        data = [
            InformationString(label="тираж", value=str(sheet_count), measurement="шт."),
            InformationString(label="на приладку", value=str(fitting_count), measurement="шт."),
        ]
        return Column(data=data)
