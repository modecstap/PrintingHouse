from decimal import Decimal
from io import BytesIO
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class FinancialReportPdfError(Exception):
    """Base error for pdf generation."""


class FinancialReportPdfCreateError(FinancialReportPdfError):
    """Raised when pdf content cannot be created."""


class FinancialReportPdfBuilder:
    """Build styled one-page pdf document from FinancialReport."""

    def __init__(self) -> None:
        """
        Initialize builder.
        """
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm

        fonts_dir = Path(__file__).parent / "fonts"
        pdfmetrics.registerFont(
            TTFont("CourierNew", str(fonts_dir / "couriercyrps.ttf"))
        )
        pdfmetrics.registerFont(
            TTFont("CourierNew-Bold", str(fonts_dir / "couriercyrps_bold.ttf"))
        )

        self._page_width, self._page_height = A4
        self._left = 14 * mm
        self._right = 14 * mm
        self._top = self._page_height - 14 * mm
        self._bottom = 14 * mm
        self._line_height = 7 * mm

        self._color_text = HexColor("#1F2937")
        self._color_muted = HexColor("#6B7280")
        self._color_line = HexColor("#D1D5DB")
        self._color_header = HexColor("#E5E7EB")

    def build(self, report: "FinancialReport") -> bytes:
        """
        Create pdf bytes from report.

        :param report: source financial report

        :raises FinancialReportPdfCreateError:

        :return: pdf content
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        try:
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=A4)
            self._draw_report(pdf, report)
            pdf.save()
            return buffer.getvalue()
        except Exception as error:
            message = "Не удалось создать pdf содержимое отчета"
            raise FinancialReportPdfCreateError(message) from error

    def _draw_report(self, pdf: "canvas.Canvas", report: "FinancialReport") -> None:
        """
        Render report content.

        :param pdf: reportlab canvas
        :param report: source report
        """
        y = self._draw_title(pdf, self._top)
        y = self._draw_period(pdf, report, y)
        rows = self._build_rows(report)
        self._draw_rows(pdf, rows, y)

    def _draw_title(self, pdf: "canvas.Canvas", y: float) -> float:
        """
        Draw document title.

        :param pdf: reportlab canvas
        :param y: current y

        :return: next y
        """
        pdf.setFillColor(self._color_text)
        pdf.setFont("CourierNew-Bold", 18)
        pdf.drawString(self._left, y, "Финансовый отчет")
        pdf.setStrokeColor(self._color_line)
        pdf.line(self._left, y - 6, self._page_width - self._right, y - 6)
        return y - 18

    def _draw_period(
        self,
        pdf: "canvas.Canvas",
        report: "FinancialReport",
        y: float,
    ) -> float:
        """
        Draw period block.

        :param pdf: reportlab canvas
        :param report: source report
        :param y: current y

        :return: next y
        """
        period = report.period.label or self._format_period(report)
        created = report.created_at.strftime("%d.%m.%Y %H:%M")

        pdf.setFont("CourierNew", 10)
        pdf.setFillColor(self._color_muted)
        pdf.drawString(self._left, y, f"Период: {period}")
        pdf.drawRightString(
            self._page_width - self._right,
            y,
            f"Создан: {created}",
        )
        return y - 18

    def _build_rows(self, report: "FinancialReport") -> list[tuple[str, str]]:
        """
        Convert report to printable rows.

        :param report: source report

        :return: printable rows
        """
        return [
            ("Выручка", self._money(report.revenue.total_revenue)),
            ("Себестоимость", self._money(report.revenue.total_cost_price)),
            (
                "Прибыль до налога",
                self._money(report.revenue.total_profit_before_tax),
            ),
            (
                "Прибыль после налога",
                self._money(report.revenue.total_profit_after_tax),
            ),
            ("Средний чек", self._money(report.revenue.average_order_value)),
            (
                "Средняя прибыль заказа",
                self._money(report.revenue.average_profit_per_order),
            ),
            ("Валовая маржа", self._percent(report.margin.gross_margin_ratio)),
            ("Чистая маржа", self._percent(report.margin.net_margin_ratio)),
            ("Средняя наценка", self._percent(report.margin.average_markup)),
            ("Количество заказов", str(report.orders.total_orders)),
            ("Прибыльных заказов", str(report.orders.profitable_orders)),
            ("Убыточных заказов", str(report.orders.unprofitable_orders)),
            ("Сумма налога", self._money(report.tax.total_tax)),
            ("Налоговая ставка", self._percent(report.tax.effective_tax_rate)),
        ]

    def _draw_rows(
        self,
        pdf: "canvas.Canvas",
        rows: list[tuple[str, str]],
        y: float,
    ) -> None:
        """
        Draw rows on page.

        :param pdf: reportlab canvas
        :param rows: printable rows
        :param y: current y
        """
        for index, (title, value) in enumerate(rows):
            if y < self._bottom:
                return

            if index % 2 == 0:
                self._draw_row_background(pdf, y)

            pdf.setFillColor(self._color_text)
            pdf.setFont("CourierNew", 10)
            pdf.drawString(self._left + 4, y, title)

            pdf.setFont("CourierNew-Bold", 10)
            pdf.drawRightString(self._page_width - self._right - 4, y, value)

            y -= self._line_height

    def _draw_row_background(self, pdf: "canvas.Canvas", y: float) -> None:
        """
        Draw soft background for row.

        :param pdf: reportlab canvas
        :param y: current y
        """
        height = self._line_height - 1
        width = self._page_width - self._left - self._right
        pdf.setFillColor(self._color_header)
        pdf.rect(self._left, y - 3, width, height, fill=1, stroke=0)

    def _format_period(self, report: "FinancialReport") -> str:
        """
        Build text period when label is empty.

        :param report: source report

        :return: text period
        """
        start = report.period.start_date.strftime("%d.%m.%Y")
        end = report.period.end_date.strftime("%d.%m.%Y")
        return f"{start} - {end}"

    def _money(self, value: Decimal) -> str:
        """
        Format money value.

        :param value: source value

        :return: formatted text
        """
        text = f"{value:,.2f}"
        return f"{text.replace(',', ' ')} Р"

    def _percent(self, value: Decimal) -> str:
        """
        Format percent value.

        :param value: source value

        :return: formatted text
        """
        return f"{value:.2f} %"
