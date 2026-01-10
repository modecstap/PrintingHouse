from fastapi import APIRouter

from backend.server.handlers.CostReportHandler import CostReportHandler


class CostReportRouter:
    def __init__(
            self,
            prefix: str = "costs_report",
            handler: CostReportHandler = CostReportHandler()
    ):
        self._prefix = f"/api/printing/{prefix}"
        self._handler = handler

        self.router = APIRouter(prefix=self._prefix, tags=[prefix])

        self._register_routes()

    def _register_routes(self):
        self.router.post("")(self._handler.take_report)
