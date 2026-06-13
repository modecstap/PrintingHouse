from fastapi import APIRouter, Depends

from backend.server.handlers.reference_production_handler import ReferenceProductionHandler
from backend.server.dependencies import get_current_user_with_full_permission, \
    get_current_user_with_read_permission


class ReferenceProductionRouter:
    """Роутер для формирования PDF-инструкции."""

    def __init__(
            self,
            prefix: str = "reference/production",
            handler: ReferenceProductionHandler = ReferenceProductionHandler()
    ):
        self._prefix = f"/api/{prefix}"
        self._handler = handler

        self.router = APIRouter(prefix=self._prefix, tags=[prefix])
        self._register_routes()

    def _register_routes(self):
        self.router.get("/", dependencies=[Depends(get_current_user_with_read_permission)])(self._handler.get)
        self.router.put("/", dependencies=[Depends(get_current_user_with_full_permission)])(self._handler.update)
