from fastapi import APIRouter

from backend.server.handlers.auth_handler import AuthHandler


class AuthRouter:
    def __init__(self, handler: AuthHandler):
        self._handler = handler

        self.router = APIRouter(
            prefix="/auth",
            tags=["auth"]
        )

        self._register_routes()

    def _register_routes(self):
        self.router.post(
            "/register",
            status_code=201
        )(self._handler.register)

        self.router.post(
            "/token",
            response_model=self._handler.token_response_model
        )(self._handler.login)