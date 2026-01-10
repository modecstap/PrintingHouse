import zipfile
from io import BytesIO

from starlette.responses import StreamingResponse

from backend.instruction_maker.instruction_builder_factory import InstructionBuilderFactory
from backend.models import Order, Printing
from backend.server.helpers.instruction_factory import InstructionService
from backend.storage.access_services.accessor_factory import AccessorFactory


class InstructionHandler:

    def take_instruction(self, order_id: int, printing: Printing) -> StreamingResponse:
        pdf_bytes = self._get_pdf_file(order_id, printing)
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=instruction.pdf"}
        )

    async def take_instruction_on_order(self, order_id: int):
        order_repository = AccessorFactory.get_order_crud_accessor()
        order: Order = await order_repository.get_model_by_id(order_id)

        zip_buffer = BytesIO()

        if len(order.printings) == 1:
            pdf_file = self._get_pdf_file(order_id, order.printings[0])
            return StreamingResponse(
                BytesIO(pdf_file),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=instruction.pdf"}
            )


        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for i, printing in enumerate(order.printings, start=1):
                pdf_bytes = self._get_pdf_file(order_id, printing)
                zip_file.writestr(f"instruction_{i}.pdf", pdf_bytes)

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=instructions.zip"}
        )

    def _get_pdf_file(self, order_id: int, printing: Printing):
        instruction_model = InstructionService().build_instruction_model(order_id, printing)
        builder = InstructionBuilderFactory(instruction_model).make_instruction_builder()
        pdf_bytes = builder.build_pdf()
        return pdf_bytes
