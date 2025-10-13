from fastapi import APIRouter

from backend.server.handlers.order_handler import OrderHandler


class OrderRouter:
    def __init__(self, prefix: str):
        self._prefix = f"/api/{prefix}"
        self._handler = OrderHandler()

        self.router = APIRouter(prefix=self._prefix, tags=[prefix])

        self._register_routes()

    def _register_routes(self):
        self.router.post("/delay")(self._handler.delay)
        self.router.post("/accept")(self._handler.accept)
        self.router.post("/status")(self._handler.change)
