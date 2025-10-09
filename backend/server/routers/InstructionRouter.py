from fastapi import APIRouter

from backend.server.handlers.InstuctionHandler import InstructionHandler


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
        self.router.post("")(self._handler.take_instruction)
