import zipfile
from io import BytesIO

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from backend.instruction_maker.instruction_builder_factory import (
    InstructionBuilderFactory,
)
from backend.models import Order, Printing
from backend.server.dependencies import (
    get_current_user_with_full_permission,
    get_current_user_with_read_permission,
)
from backend.server.helpers.instruction_factory import InstructionService
from backend.storage.access_services.accessor_factory import AccessorFactory


router = APIRouter(prefix="/api/instruction", tags=["instruction"])


def _build_pdf(order_id: int, unit_count: int, printing: Printing) -> bytes:
    instruction_model = InstructionService().build_instruction_model(
        order_id,
        unit_count,
        printing,
    )
    builder = InstructionBuilderFactory(instruction_model).make_instruction_builder()
    return builder.build_pdf()


@router.get(
    "/{order_id}",
    dependencies=[Depends(get_current_user_with_read_permission)],
)
async def get_order_instruction(order_id: int) -> StreamingResponse:
    """Возвращает инструкцию сохранённого заказа.

    Результат: instruction.pdf, если печать одна, иначе instructions.zip.
    Ошибки: NotFoundException, если заказа нет. Здесь она не перехватывается.
    """
    order_repository = AccessorFactory.get_order_crud_accessor()
    order: Order = await order_repository.get_model_by_id(order_id)

    if len(order.printings) == 1:
        pdf_bytes = _build_pdf(order_id, order.unit_count, order.printings[0])
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=instruction.pdf"},
        )

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for i, printing in enumerate(order.printings, start=1):
            pdf_bytes = _build_pdf(order_id, order.unit_count, printing)
            zip_file.writestr(f"instruction_{i}.pdf", pdf_bytes)

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=instructions.zip"},
    )


@router.post(
    "",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def build_instruction(
    order_id: int,
    unit_count: int,
    printing: Printing,
) -> StreamingResponse:
    """Собирает PDF-инструкцию по параметрам запроса и телу Printing.

    Результат: файл instruction.pdf.
    """
    pdf_bytes = _build_pdf(order_id, unit_count, printing)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=instruction.pdf"},
    )
