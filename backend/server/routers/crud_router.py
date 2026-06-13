from fastapi import APIRouter, Depends

from backend.server.handlers.entity_handler import EntityHandler
from backend.server.dependencies import get_current_user_with_full_permission, \
    get_current_user_with_read_permission


class CRUDRouter:
    def __init__(self, prefix: str, handler: EntityHandler):
        self._prefix = f"/api/{prefix}"
        self._handler = handler

        self.router = APIRouter(prefix=self._prefix, tags=[prefix])

        self._register_routes()

    def _register_routes(self):
        self.router.get("/", dependencies=[Depends(get_current_user_with_read_permission)])(self._handler.get_all)
        self.router.get("/{id}", dependencies=[Depends(get_current_user_with_read_permission)])(self._handler.get)
        self.router.post("/", dependencies=[Depends(get_current_user_with_full_permission)])(self._handler.create)
        self.router.post("/bulk", dependencies=[Depends(get_current_user_with_full_permission)])(self._handler.create_bulk)
        self.router.put("/{id}", dependencies=[Depends(get_current_user_with_full_permission)])(self._handler.update)
        self.router.put("/", dependencies=[Depends(get_current_user_with_full_permission)])(self._handler.update_bulk)
        self.router.delete("/{id}", dependencies=[Depends(get_current_user_with_full_permission)])(self._handler.delete)
