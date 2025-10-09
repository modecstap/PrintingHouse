from reportlab.lib import colors
from reportlab.pdfgen import canvas

from backend.instruction_maker.steps.information_string import InformationString


class Column:
    def __init__(
            self,
            data: list[InformationString],
            title_font: str = "CourierNew",
            label_font: str = "CourierNew",
            value_font: str = "CourierNew-Bold",
    ):
        self._data = data
        self.title_font = title_font
        self.label_font = label_font
        self.value_font = value_font

        self.horizontal_shift = 0
        self.vertical_shift = 0

        # Настраиваем отступы и интервалы
        self.line_height = 20
        self.block_spacing = 10

    def render(self, pdf: canvas.Canvas, y: float, x: float):
        """Отрисовка заголовка и информации с улучшенной визуализацией."""
        self.vertical_shift = y
        self.horizontal_shift = x
        self._draw_lines(pdf)

    def _draw_lines(self, pdf: canvas.Canvas):
        for info in self._data:
            # Лейбл
            pdf.setFont(self.label_font, 14)
            pdf.drawString(
                self.horizontal_shift + 40,
                self.vertical_shift,
                f"{info.label}:"
            )
            self.vertical_shift -= self.line_height

            # Значение (жирное и чуть больше)
            pdf.setFont(self.value_font, 14)
            pdf.drawString(
                self.horizontal_shift + 45,
                self.vertical_shift,
                info.value
            )

            # Единица измерения
            if info.measurement:
                value_width = pdf.stringWidth(info.value, self.value_font, 14)
                pdf.setFont(self.label_font, 12)
                pdf.drawString(
                    self.horizontal_shift + 45 + value_width + 5,
                    self.vertical_shift,
                    info.measurement
                )

            # Лёгкая направляющая линия (опционально)
            pdf.setStrokeColor(colors.lightgrey)
            pdf.setLineWidth(0.3)
            pdf.line(
                self.horizontal_shift + 35,
                self.vertical_shift - 4,
                self.horizontal_shift + 200,
                self.vertical_shift - 4
            )

            # Переход к следующему блоку
            self.vertical_shift -= self.line_height + self.block_spacing
