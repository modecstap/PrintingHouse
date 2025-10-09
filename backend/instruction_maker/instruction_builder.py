from datetime import datetime
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from backend.instruction_maker.steps.column import Column


class InstructionBuilder:
    def __init__(self, columns: list[Column], order_id: int):
        self._columns = columns
        self._order_id = order_id

        fonts_dir = Path(__file__).parent / "fonts"
        pdfmetrics.registerFont(TTFont("CourierNew", str(fonts_dir / "couriercyrps.ttf")))
        pdfmetrics.registerFont(TTFont("CourierNew-Bold", str(fonts_dir / "couriercyrps_bold.ttf")))

        self._width, self._height = A4

    def build_pdf(self) -> bytes:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)

        margin = 20  # отступ от края листа
        self._create_frame(margin, pdf)

        cell_height = 30
        start_y = self._height - margin - cell_height

        self._create_header(cell_height, margin, pdf, start_y)

        self._create_body(pdf, start_y)

        self._create_footer(margin, pdf)

        # === ЗАВЕРШЕНИЕ ===
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer.read()

    def _create_footer(self, margin, pdf):
        bottom_y = margin
        bottom_cell_height = 25
        bottom_cell_width = (self._width - 2 * margin) / 2
        pdf.setLineWidth(1)
        pdf.setStrokeColor(colors.black)
        pdf.rect(margin, bottom_y, bottom_cell_width, bottom_cell_height)
        pdf.rect(margin + bottom_cell_width, bottom_y, bottom_cell_width, bottom_cell_height)
        pdf.setFont("CourierNew", 14)
        date_str = datetime.now().strftime("%d.%m.%Y")
        pdf.drawString(margin + 10, bottom_y + 8, f"{date_str}")
        pdf.drawString(margin + bottom_cell_width + 10, bottom_y + 8, "Подпись: ____________")

    def _create_body(self, pdf, start_y):
        pdf.setFont("CourierNew", 12)
        vertical_shift = start_y - 40
        horizontal_shift = 10
        for column in self._columns:
            column.render(pdf, vertical_shift, horizontal_shift)
            horizontal_shift += 250

    def _create_header(self, cell_height, margin, pdf, start_y):
        cell_widths = [150, self._width - 150 - 150 - 2 * margin, 150]
        x = margin
        for i, text in enumerate(["Техкарта", "", f"Заказ № {self._order_id}"]):
            pdf.rect(x, start_y, cell_widths[i], cell_height)
            if text:
                pdf.setFont("CourierNew", 14)
                text_y = start_y + 8
                text_x = x + 10
                pdf.drawString(text_x, text_y, text)
            x += cell_widths[i]

    def _create_frame(self, margin, pdf):
        pdf.setLineWidth(1)
        pdf.rect(margin, margin, self._width - 2 * margin, self._height - 2 * margin)


if __name__ == "__main__":
    from backend.instruction_maker.steps.column_factory import ColumnFactory
    from backend.models import Chroma, Lamination, PressSheet, ListSize

    steps = [
        ColumnFactory().create_print_information(300, PressSheet(width=450, height=320, spacing=5), Chroma(3),
                                                 Lamination(1), False),
        ColumnFactory().create_edition_information(200, 5, 400, ListSize(width=300, height=200, bleeds=2), 2),
    ]

    builder = InstructionBuilder(steps, order_id=157)
    pdf_bytes = builder.build_pdf()

    output_path = "test_instruction.pdf"
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"✅ PDF-инструкция успешно создана: {output_path}")
