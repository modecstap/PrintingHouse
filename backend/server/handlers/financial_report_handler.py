from datetime import datetime
from io import BytesIO

from starlette.responses import StreamingResponse

from backend.financial_reporter.financial_mediator import FinancialMediator
from backend.financial_reporter.financial_report_pdf_builder import \
    FinancialReportPdfBuilder
from backend.models.financial_report import ReportPeriod


class FinancialReportHandler:

    def __init__(self):
        self._reporter = FinancialReportPdfBuilder()
        self._mediator = FinancialMediator()

    async def take_report(self, start: datetime, end: datetime):
        period = ReportPeriod(
            start_date=start,
            end_date=end
        )
        report = await self._mediator.get_report(period)
        pdf_file = self._reporter.build(report)
        return StreamingResponse(
            BytesIO(pdf_file),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=financial-report.pdf"}
        )
