from fastapi import APIRouter, Depends

from backend.server.handlers.order_handler import OrderHandler
from backend.server.dependencies import get_current_user_with_full_permission


class OrderRouter:
    def __init__(self, prefix: str):
        self._prefix = f"/api/{prefix}"
        self._handler = OrderHandler()

        self.router = APIRouter(prefix=self._prefix, tags=[prefix])

        self._register_routes()

    def _register_routes(self):
        self.router.post("/cost_report", dependencies=[Depends(get_current_user_with_full_permission)])(self._handler.cost_report)
        self.router.post("/delay", dependencies=[Depends(get_current_user_with_full_permission)])(self._handler.delay)
        self.router.post("/accept", dependencies=[Depends(get_current_user_with_full_permission)])(self._handler.accept)
        self.router.post("/status", dependencies=[Depends(get_current_user_with_full_permission)])(self._handler.change)
