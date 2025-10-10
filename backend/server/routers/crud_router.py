from fastapi import APIRouter

from backend.server.handlers.entity_handler import EntityHandler


class CRUDRouter:
    def __init__(self, prefix: str, handler: EntityHandler):
        self._prefix = f"/api/{prefix}"
        self._handler = handler

        self.router = APIRouter(prefix=self._prefix, tags=[prefix])

        self._register_routes()

    def _register_routes(self):
        self.router.get("/")(self._handler.get_all)
        self.router.get("/{id}")(self._handler.get)
        self.router.post("/")(self._handler.create)
        self.router.post("/bulk")(self._handler.create_bulk)
        self.router.put("/{id}")(self._handler.update)
        self.router.put("/")(self._handler.update_bulk)
        self.router.delete("/{id}")(self._handler.delete)
