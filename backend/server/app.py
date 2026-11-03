import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.storage.database import Database
from backend.storage.db_config import DBConfig

# Репозитории маршрутов вызывают Database(None) и берут синглтон.
# Синглтон собирается здесь из env. main перед serve только ждёт
# соединение и таблицы не создаёт.
Database(DBConfig.from_env())

from backend.server.auth.routes import router as auth_router
from backend.server.server_config import ServerConfig
from backend.server.sheet import (
    bind_sheet_service,
    router as sheet_router,
)
from backend.server.workplace_order import (
    bind_workplace_order_service,
    router as workplace_order_router,
)
from backend.server.workplace_reference import (
    router as workplace_reference_router,
)
from backend.core.administrator import Administrator
from backend.core.order_service import WorkplaceOrderService
from backend.core.sheet.service import SheetService
from backend.storage.repositories.sheet_repository import (
    SqlSheetRepository,
)
from backend.storage.repositories.workplace_order_repository import (
    SqlWorkplaceOrderRepository,
)
from backend.storage.sync_engine import create_sync_engine

# Маршруты не импортируют backend.storage.sync_engine, поэтому Engine
# создаётся здесь, один раз на процесс. Один репозиторий листа идёт
# и в сервис листа, и в сервис заказа.
_engine = create_sync_engine()
_sheets = SqlSheetRepository(_engine)
bind_workplace_order_service(
    WorkplaceOrderService(
        SqlWorkplaceOrderRepository(_engine),
        _sheets,
        Administrator(),
    )
)
bind_sheet_service(SheetService(_sheets))


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(workplace_order_router)
app.include_router(sheet_router)
app.include_router(workplace_reference_router)
app.include_router(auth_router)


async def serve(config: ServerConfig) -> None:
    """Listens for HTTP on the host and port from config until the process is stopped.

    :param config: the host and port.
    """
    server = uvicorn.Config(
        app,
        host=config.host,
        port=config.port,
        loop="asyncio",
    )
    await uvicorn.Server(server).serve()
