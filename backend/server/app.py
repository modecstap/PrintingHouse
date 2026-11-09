"""FastAPI application factory and uvicorn serve."""

from __future__ import annotations

import logging
import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.auth import AuthConfig
from backend.new_core.application_services.order import OrderIdAllocationFailed
from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.errors import InvalidInput, InvalidPriceException
from backend.new_core.order.repository import OrderNotFound
from backend.server.auth import router as auth_router
from backend.server.equipment import router as equipment_router
from backend.server.orders import router as orders_router
from backend.server.references import router as references_router
from backend.server.staff import router as staff_router
from backend.server.server_config import ServerConfig
from backend.storage.database import Database
from backend.storage.db_config import DBConfig

_logger = logging.getLogger("backend.http")


def _validation_detail(exc: RequestValidationError) -> str:
    parts: list[str] = []
    for error in exc.errors():
        loc = ".".join(str(part) for part in error.get("loc", ()))
        msg = error.get("msg", "")
        parts.append(f"{loc}: {msg}")
    return "; ".join(parts)


def create_app(auth_config: AuthConfig, database: Database) -> FastAPI:
    """Builds the API application with routers and exception handlers.

    :param auth_config:
    :param database:

    :return: configured FastAPI instance.
    """
    app = FastAPI(debug=False)
    app.state.auth_config = auth_config
    app.state.database = database

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        status = response.status_code
        path = request.url.path
        message = (
            f"{request.method} {path} status={status} duration_ms={duration_ms:.1f}"
        )
        if 200 <= status < 300:
            _logger.info(message)
        elif 400 <= status < 500:
            _logger.warning(message)
        else:
            _logger.error(message)
        return response

    @app.exception_handler(InvalidInput)
    @app.exception_handler(InvalidPriceException)
    async def unprocessable(_request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(OrderNotFound)
    async def order_not_found(_request: Request, exc: OrderNotFound) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(KeyError)
    async def catalog_miss(_request: Request, exc: KeyError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(OrderIdAllocationFailed)
    async def order_id_conflict(
        _request: Request,
        exc: OrderIdAllocationFailed,
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(CatalogIdOccupied)
    async def catalog_id_conflict(
        _request: Request,
        exc: CatalogIdOccupied,
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(TypeError)
    async def unsupported_operation(
        _request: Request,
        exc: TypeError,
    ) -> JSONResponse:
        text = str(exc)
        if text.startswith("Unsupported run operation type:"):
            return JSONResponse(status_code=400, content={"detail": text})
        raise exc

    @app.exception_handler(RequestValidationError)
    async def request_validation(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": _validation_detail(exc)},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": detail},
            headers=exc.headers,
        )

    app.include_router(auth_router)
    app.include_router(orders_router)
    app.include_router(references_router)
    app.include_router(equipment_router)
    app.include_router(staff_router)
    return app


async def serve(
    config: ServerConfig,
    *,
    auth_config: AuthConfig | None = None,
    database: Database | None = None,
) -> None:
    """Runs uvicorn until shutdown.

    :param config:
    :param auth_config: when omitted, loads from environment.
    :param database: when omitted, builds from environment.
    """
    if auth_config is None:
        auth_config = AuthConfig.from_env()
    if database is None:
        database = Database(DBConfig.from_env())
    app = create_app(auth_config, database)
    uvicorn_config = uvicorn.Config(
        app,
        host=config.host,
        port=config.port,
        loop="asyncio",
    )
    server = uvicorn.Server(uvicorn_config)
    await server.serve()
