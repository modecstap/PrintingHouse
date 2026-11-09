"""FastAPI dependencies for DB sessions and application services."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.auth import AuthConfig, CredentialsError, username_from_token
from backend.new_core.application_services.equipment import EquipmentCatalogService
from backend.new_core.application_services.materials import MaterialCatalogService
from backend.new_core.application_services.order import OrderService
from backend.new_core.application_services.personal import StaffCatalogService
from backend.new_core.application_services.reference import ReferenceOrderService
from backend.storage.database import Database
from backend.storage.materials.film_repository import SqlFilmRepository
from backend.storage.materials.sheet_repository import SqlSheetRepository
from backend.storage.equipment.cutter_repository import SqlCutterRepository
from backend.storage.equipment.laminator_repository import SqlLaminatorRepository
from backend.storage.equipment.printer_repository import SqlPrinterRepository
from backend.storage.order.repository import SqlOrderRepository
from backend.storage.order.unit_of_work import SqlOrderUnitOfWork
from backend.storage.personal.cutter_operator_repository import SqlCutterOperatorRepository
from backend.storage.personal.die_cutter_operator_repository import (
    SqlDieCutterOperatorRepository,
)
from backend.storage.personal.laminator_operator_repository import (
    SqlLaminatorOperatorRepository,
)
from backend.storage.personal.press_operator_repository import SqlPressOperatorRepository
from backend.storage.reference.repository import SqlReferenceRepository
from backend.storage.user.repository import SqlUserRepository

_bearer = HTTPBearer(auto_error=False)


def get_database(request: Request) -> Database:
    """Returns the app database handle."""
    return request.app.state.database


def get_auth_config(request: Request) -> AuthConfig:
    """Returns JWT settings stored on the app."""
    return request.app.state.auth_config


def get_db_session(
    database: Annotated[Database, Depends(get_database)],
) -> Generator[Session, None, None]:
    """Opens one SQLAlchemy session per request.

    :param database:

    :yield: request-scoped session.
    """
    session = database.session_factory()
    try:
        yield session
    finally:
        session.close()


def get_user_store(
    session: Annotated[Session, Depends(get_db_session)],
) -> SqlUserRepository:
    """Returns the SQL user repository for this request."""
    return SqlUserRepository(session)


def get_order_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> OrderService:
    """Builds :class:`OrderService` for this request."""
    uow = SqlOrderUnitOfWork(session)
    return OrderService(
        uow,
        SqlPrinterRepository(session),
        SqlPressOperatorRepository(session),
        SqlLaminatorRepository(session),
        SqlLaminatorOperatorRepository(session),
        SqlCutterRepository(session),
        SqlCutterOperatorRepository(session),
        SqlDieCutterOperatorRepository(session),
    )


def get_reference_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> ReferenceOrderService:
    """Builds :class:`ReferenceOrderService` for this request."""
    return ReferenceOrderService(
        SqlReferenceRepository(session),
        SqlOrderRepository(session),
    )


def get_equipment_catalog_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> EquipmentCatalogService:
    """Builds :class:`EquipmentCatalogService` for this request."""
    return EquipmentCatalogService(
        SqlPrinterRepository(session),
        SqlLaminatorRepository(session),
        SqlCutterRepository(session),
    )


def get_material_catalog_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> MaterialCatalogService:
    """Builds :class:`MaterialCatalogService` for this request."""
    return MaterialCatalogService(
        SqlFilmRepository(session),
        SqlSheetRepository(session),
    )


def get_staff_catalog_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> StaffCatalogService:
    """Builds :class:`StaffCatalogService` for this request."""
    return StaffCatalogService(
        SqlPressOperatorRepository(session),
        SqlLaminatorOperatorRepository(session),
        SqlCutterOperatorRepository(session),
        SqlDieCutterOperatorRepository(session),
    )


def require_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer),
    ],
    auth_config: Annotated[AuthConfig, Depends(get_auth_config)],
) -> str:
    """Validates Bearer JWT and returns the username.

    :raises HTTPException: 401 when credentials are missing or invalid.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return username_from_token(credentials.credentials, auth_config)
    except CredentialsError as exc:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
