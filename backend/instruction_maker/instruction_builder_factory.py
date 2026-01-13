from backend.instruction_maker.instruction_builder import InstructionBuilder
from backend.instruction_maker.instruction_model import InstructionModel
from backend.instruction_maker.steps.column_factory import ColumnFactory


class InstructionBuilderFactory:

    def __init__(
            self,
            instruction_model: InstructionModel,
            column_factory: ColumnFactory = ColumnFactory()
    ):
        self._factory = column_factory
        self._instruction = instruction_model

    def make_instruction_builder(self) -> InstructionBuilder:
        columns = [
            self._factory.create_print_information(
                density=self._instruction.density,
                press_sheet=self._instruction.press_sheet,
                chroma=self._instruction.chroma,
                lamination=self._instruction.lamination,
                die_cutting=self._instruction.die_cutting
            ),
            self._factory.create_edition_information(
                sheet_count=self._instruction.sheet_count,
                fitting_count=self._instruction.fitting_count,
                edition_count=self._instruction.edition_count,
                list_size=self._instruction.list_size,
                product_per_sheet=self._instruction.product_per_sheet,
                unit_count=self._instruction.unit_count
            )
        ]

        return InstructionBuilder(
            columns=columns,
            order_id=self._instruction.order_id,
            comment=self._instruction.comment
        )
