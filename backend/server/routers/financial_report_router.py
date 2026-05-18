from fastapi import APIRouter

from backend.server.handlers.financial_report_handler import \
    FinancialReportHandler


class FinancialReportRouter:

    def __init__(
            self,
            prefix: str = "financial",
            handler: FinancialReportHandler = FinancialReportHandler()
    ):
        self._prefix = f"/api/{prefix}"
        self._handler = handler

        self.router = APIRouter(prefix=self._prefix, tags=[prefix])
        self._register_routes()

    def _register_routes(self):
        self.router.get("/")(self._handler.take_report)
