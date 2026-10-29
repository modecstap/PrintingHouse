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
from backend.server.workplace_order import (
    bind_workplace_order_service,
    router as workplace_order_router,
)
from backend.server.workplace_reference import (
    router as workplace_reference_router,
)
from backend.workplace.administrator import Administrator
from backend.workplace.order_service import WorkplaceOrderService
from backend.workplace_order_db import (
    SqlWorkplaceOrderRepository,
    create_sync_engine,
)

# Маршруты не импортируют workplace_order_db, поэтому Engine
# создаётся здесь, один раз на процесс.
bind_workplace_order_service(
    WorkplaceOrderService(
        SqlWorkplaceOrderRepository(create_sync_engine()),
        Administrator(),
    )
)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(workplace_order_router)
app.include_router(workplace_reference_router)
app.include_router(auth_router)


async def serve(config: ServerConfig) -> None:
    """Слушает HTTP на host и port из config, пока процесс не остановят.

    Побочные эффекты: блокирует текущую задачу на uvicorn.
    """
    server = uvicorn.Config(
        app,
        host=config.host,
        port=config.port,
        loop="asyncio",
    )
    await uvicorn.Server(server).serve()
