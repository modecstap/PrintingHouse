from io import BytesIO

from starlette.responses import StreamingResponse

from backend.instruction_maker.instruction_builder_factory import InstructionBuilderFactory
from backend.instruction_maker.instruction_data import InstructionModel


class InstructionHandler:

    def take_instruction(self, instruction_model: InstructionModel) -> StreamingResponse:
        factory = InstructionBuilderFactory(instruction_model=instruction_model)

        builder = factory.make_instruction_builder()
        pdf_bytes = builder.build_pdf()
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=instruction.pdf"}
        )
