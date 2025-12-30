from fastapi import APIRouter

from backend.server.handlers.reference_production_handler import ReferenceProductionHandler


class ReferenceProductionRouter:
    """Роутер для формирования PDF-инструкции."""

    def __init__(
            self,
            prefix: str = "reference-production",
            handler: ReferenceProductionHandler = ReferenceProductionHandler()
    ):
        self._prefix = f"/api/{prefix}"
        self._handler = handler

        self.router = APIRouter(prefix=self._prefix, tags=[prefix])
        self._register_routes()

    def _register_routes(self):
        self.router.get("/")(self._handler.get)
        self.router.put("/")(self._handler.update)
