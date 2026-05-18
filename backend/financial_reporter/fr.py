from io import BytesIO
from decimal import Decimal
from statistics import mean

from reportlab.lib.pagesizes import A4
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing, String
from reportlab.pdfgen.canvas import Canvas

from backend.models.financial_report import FinancialReport


class FinancialReportPdfBuilderError(Exception):
    """Base builder error."""


class FinancialReportPdfBuildError(FinancialReportPdfBuilderError):
    """Raised when pdf build failed."""


class FinancialReportPdfBuilder:
    """
    Build PDF document for financial reports.
    """

    def __init__(self, reports: list[FinancialReport]) -> None:
        """
        Create builder instance.
        """
        self._buffer = BytesIO()
        self._canvas = Canvas(self._buffer, pagesize=A4)
        self._width, self._height = A4
        self._reports = reports

    def add_reports(self, report_page_builder: ) -> "FinancialReportPdfBuilder":
        """
        Add report pages.

        :return: self
        """
        for report in self._reports:
            self._draw_report_page(report)
            self._canvas.showPage()
        return self

    def add_summary(self) -> "FinancialReportPdfBuilder":
        """
        Add summary charts page.

        :return: self
        """
        if not self._reports:
            return self

        metrics = self._collect_summary_metrics()
        self._draw_summary_page(metrics)
        self._canvas.showPage()
        return self

    def build(self) -> bytes:
        """
        Build pdf bytes.

        :raises FinancialReportPdfBuildError:

        :return: pdf content
        """
        try:
            self._canvas.save()
            return self._buffer.getvalue()
        except Exception as error:
            raise FinancialReportPdfBuildError(str(error)) from error

    def _draw_report_page(self, report) -> None:
        """
        Draw single report page.

        :param report: financial report
        """
        self._canvas.setFont("Helvetica-Bold", 14)
        self._canvas.drawString(40, 800, "Финансовый отчёт")
        self._canvas.setFont("Helvetica", 10)
        self._canvas.drawString(40, 780, report.period.label)
        self._draw_section(750, "Выручка", report.revenue)
        self._draw_section(610, "Маржинальность", report.margin)
        self._draw_section(520, "Экономика", report.unit_economics)
        self._draw_section(430, "Заказы", report.orders)
        self._draw_section(360, "Налоги", report.tax)

    def _draw_section(self, top: int, title: str, model) -> None:
        """
        Draw model fields.

        :param top: y coordinate
        :param title: section title
        :param model: pydantic model
        """
        self._canvas.setFont("Helvetica-Bold", 11)
        self._canvas.drawString(40, top, title)
        self._canvas.setFont("Helvetica", 9)
        y_position = top - 18
        for key, value in model.model_dump().items():
            line = f"{key}: {value}"
            self._canvas.drawString(50, y_position, line[:95])
            y_position -= 14

    def _collect_summary_metrics(self) -> dict:
        """
        Aggregate metrics by month.

        :return: metrics values
        """
        grouped = {}
        for report in self._reports:
            month = report.period.start_date.strftime("%Y-%m")
            data = grouped.setdefault(month, {})
            self._append_metric(data, "revenue", report.revenue.total_revenue)
            self._append_metric(data, "profit", report.revenue.total_profit_after_tax)
            self._append_metric(data, "orders", report.orders.total_orders)
        return self._build_averages(grouped)

    def _append_metric(self, data: dict, name: str, value) -> None:
        """
        Append metric value.

        :param data: month data
        :param name: metric name
        :param value: metric value
        """
        data.setdefault(name, []).append(float(value))

    def _build_averages(self, grouped: dict) -> dict:
        """
        Convert lists to averages.

        :param grouped: grouped values

        :return: averages
        """
        result = {}
        for month, values in grouped.items():
            result[month] = {
                key: mean(items) for key, items in values.items()
            }
        return result

    def _draw_summary_page(self, metrics: dict) -> None:
        """
        Draw summary page.

        :param metrics: aggregated metrics
        """
        self._canvas.setFont("Helvetica-Bold", 14)
        self._canvas.drawString(40, 800, "Сводная аналитика")
        self._draw_chart(40, 520, "Выручка", metrics, "revenue")
        self._draw_chart(40, 300, "Прибыль", metrics, "profit")
        self._draw_chart(40, 80, "Заказы", metrics, "orders")

    def _draw_chart(
        self,
        left: int,
        bottom: int,
        title: str,
        metrics: dict,
        field_name: str,
    ) -> None:
        """
        Draw bar chart.

        :param left: x coordinate
        :param bottom: y coordinate
        :param title: chart title
        :param metrics: source data
        :param field_name: metric field
        """
        months = sorted(metrics.keys())
        values = [metrics[item][field_name] for item in months]
        drawing = Drawing(500, 180)
        drawing.add(String(0, 165, title, fontSize=12))
        chart = VerticalBarChart()
        chart.x = 40
        chart.y = 20
        chart.height = 120
        chart.width = 420
        chart.data = [values]
        chart.categoryAxis.categoryNames = months
        drawing.add(chart)
        drawing.drawOn(self._canvas, left, bottom)