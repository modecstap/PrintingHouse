import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.server.handlers.order_handler import OrderHandler
from backend.server.routers.CostReportRouter import CostReportRouter
from backend.server.routers.InstructionRouter import InstructionRouter
from backend.server.routers.crud_router import CRUDRouter
from backend.server.routers.order_router import OrderRouter
from backend.server.routers.reference_production_router import ReferenceProductionRouter
from backend.server.server_config import ServerConfig


class FastAPIServer:
    def __init__(self, config: ServerConfig):
        self._config = config
        self.app = FastAPI()
        self.server: uvicorn.Server = None

        self._setup_cors()
        self._setup_routes()

    def _setup_cors(self):
        origins = [
            "*"
        ]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    async def start(self):
        config = uvicorn.Config(self.app, host=self._config.host, port=self._config.port, loop="asyncio")
        self.server = uvicorn.Server(config)
        await self.server.serve()

    async def stop(self):
        if self.server:
            self.server.should_exit = True

    def _setup_routes(self):
        self.app.include_router(CostReportRouter().router)
        self.app.include_router(InstructionRouter().router)
        self.app.include_router(ReferenceProductionRouter().router)
        self.app.include_router(CRUDRouter("order", OrderHandler()).router)
        self.app.include_router(OrderRouter("order").router)
