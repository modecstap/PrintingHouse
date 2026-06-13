from fastapi import APIRouter, Depends

from backend.server.handlers.instruction_handler import InstructionHandler
from backend.server.dependencies import get_current_user_with_full_permission, \
    get_current_user_with_read_permission


class InstructionRouter:
    """Роутер для формирования PDF-инструкции."""

    def __init__(
            self,
            prefix: str = "instruction",
            handler: InstructionHandler = InstructionHandler()
    ):
        self._prefix = f"/api/{prefix}"
        self._handler = handler

        self.router = APIRouter(prefix=self._prefix, tags=[prefix])
        self._register_routes()

    def _register_routes(self):
        self.router.get("/{order_id}", dependencies=[Depends(get_current_user_with_read_permission)])(self._handler.take_instruction_on_order)
        self.router.post("", dependencies=[Depends(get_current_user_with_full_permission)])(self._handler.take_instruction)
