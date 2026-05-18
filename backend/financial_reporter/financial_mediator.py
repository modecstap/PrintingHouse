from backend.financial_reporter.financial_reporter import FinancialReporter
from backend.models.financial_report import FinancialReport, ReportPeriod
from backend.storage.access_services.accessor_factory import AccessorFactory


class FinancialMediator:
    def __init__(self):
        self._repository = AccessorFactory.get_order_crud_accessor()

    async def get_report(self, period: ReportPeriod) -> FinancialReport:
        orders = await self._repository.get_models()
        reporter = FinancialReporter(orders)
        return reporter.build(period)
