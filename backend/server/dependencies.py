"""FastAPI dependencies for DB sessions and application services."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.auth import AuthConfig, CredentialsError, username_from_token
from backend.new_core.accountant.pricing.factory import PricingStrategyFactory
from backend.new_core.application_services.equipment.cutters import (
    CutterCatalog,
)
from backend.new_core.application_services.equipment.laminators import (
    LaminatorCatalog,
)
from backend.new_core.application_services.equipment.printers import (
    PrinterCatalog,
)
from backend.new_core.application_services.materials.films import FilmCatalog
from backend.new_core.application_services.materials.sheets import SheetCatalog
from backend.new_core.application_services.personal.cutter_operators import (
    CutterOperatorCatalog,
)
from backend.new_core.application_services.personal.die_cut_operators import (
    DieCutterOperatorCatalog,
)
from backend.new_core.application_services.personal.laminator_operators import (
    LaminatorOperatorCatalog,
)
from backend.new_core.application_services.personal.press_operators import (
    PressOperatorCatalog,
)
from backend.new_core.equipment.factory import (
    CutterFactory,
    LaminatorFactory,
    PrinterFactory,
)
from backend.new_core.order.factory import OrderFactory
from backend.new_core.personal.factory import (
    CutterOperatorFactory,
    DieCutterOperatorFactory,
    LaminatorOperatorFactory,
    PressOperatorFactory,
)
from backend.new_core.print_run.factory import PrintRunFactory
from backend.new_core.application_services.order import OrderService
from backend.new_core.application_services.reference import (
    ReferenceOrderService,
)
from backend.storage.database import Database
from backend.storage.materials.film_repository import SqlFilmRepository
from backend.storage.materials.sheet_repository import SqlSheetRepository
from backend.storage.equipment.cutter_repository import SqlCutterRepository
from backend.storage.equipment.laminator_repository import (
    SqlLaminatorRepository,
)
from backend.storage.equipment.printer_repository import SqlPrinterRepository
from backend.storage.order.repository import SqlOrderRepository
from backend.storage.order.unit_of_work import SqlOrderUnitOfWork
from backend.storage.personal.cutter_operator_repository import (
    SqlCutterOperatorRepository,
)
from backend.storage.personal.die_cutter_operator_repository import (
    SqlDieCutterOperatorRepository,
)
from backend.storage.personal.laminator_operator_repository import (
    SqlLaminatorOperatorRepository,
)
from backend.storage.personal.press_operator_repository import (
    SqlPressOperatorRepository,
)
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
) -> Generator[Session]:
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
        OrderFactory(uow.orders),
        PrintRunFactory(uow.print_runs),
        PricingStrategyFactory(
            SqlPrinterRepository(session),
            SqlPressOperatorRepository(session),
            SqlLaminatorRepository(session),
            SqlLaminatorOperatorRepository(session),
            SqlCutterRepository(session),
            SqlCutterOperatorRepository(session),
            SqlDieCutterOperatorRepository(session),
            SqlFilmRepository(session),
        ),
    )


def get_reference_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> ReferenceOrderService:
    """Builds :class:`ReferenceOrderService` for this request."""
    return ReferenceOrderService(
        SqlReferenceRepository(session),
        SqlOrderRepository(session),
    )


def get_printer_catalog(
    session: Annotated[Session, Depends(get_db_session)],
) -> PrinterCatalog:
    """Builds :class:`PrinterCatalog` for this request."""
    printers = SqlPrinterRepository(session)
    return PrinterCatalog(printers, PrinterFactory(printers))


def get_laminator_catalog(
    session: Annotated[Session, Depends(get_db_session)],
) -> LaminatorCatalog:
    """Builds :class:`LaminatorCatalog` for this request."""
    laminators = SqlLaminatorRepository(session)
    return LaminatorCatalog(laminators, LaminatorFactory(laminators))


def get_cutter_catalog(
    session: Annotated[Session, Depends(get_db_session)],
) -> CutterCatalog:
    """Builds :class:`CutterCatalog` for this request."""
    cutters = SqlCutterRepository(session)
    return CutterCatalog(cutters, CutterFactory(cutters))


def get_film_catalog(
    session: Annotated[Session, Depends(get_db_session)],
) -> FilmCatalog:
    """Builds :class:`FilmCatalog` for this request."""
    return FilmCatalog(SqlFilmRepository(session))


def get_sheet_catalog(
    session: Annotated[Session, Depends(get_db_session)],
) -> SheetCatalog:
    """Builds :class:`SheetCatalog` for this request."""
    return SheetCatalog(SqlSheetRepository(session))


def get_press_operator_catalog(
    session: Annotated[Session, Depends(get_db_session)],
) -> PressOperatorCatalog:
    """Builds :class:`PressOperatorCatalog` for this request."""
    press_operators = SqlPressOperatorRepository(session)
    return PressOperatorCatalog(
        press_operators,
        PressOperatorFactory(press_operators),
    )


def get_laminator_operator_catalog(
    session: Annotated[Session, Depends(get_db_session)],
) -> LaminatorOperatorCatalog:
    """Builds :class:`LaminatorOperatorCatalog` for this request."""
    laminator_operators = SqlLaminatorOperatorRepository(session)
    return LaminatorOperatorCatalog(
        laminator_operators,
        LaminatorOperatorFactory(laminator_operators),
    )


def get_cutter_operator_catalog(
    session: Annotated[Session, Depends(get_db_session)],
) -> CutterOperatorCatalog:
    """Builds :class:`CutterOperatorCatalog` for this request."""
    cutter_operators = SqlCutterOperatorRepository(session)
    return CutterOperatorCatalog(
        cutter_operators,
        CutterOperatorFactory(cutter_operators),
    )


def get_die_cut_operator_catalog(
    session: Annotated[Session, Depends(get_db_session)],
) -> DieCutterOperatorCatalog:
    """Builds :class:`DieCutterOperatorCatalog` for this request."""
    die_cut_operators = SqlDieCutterOperatorRepository(session)
    return DieCutterOperatorCatalog(
        die_cut_operators,
        DieCutterOperatorFactory(die_cut_operators),
    )


def get_printer_catalog_and_session(
    catalog: Annotated[PrinterCatalog, Depends(get_printer_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> tuple[PrinterCatalog, Session]:
    """Returns printer catalog and request session for replace routes."""
    return catalog, session


def get_laminator_catalog_and_session(
    catalog: Annotated[LaminatorCatalog, Depends(get_laminator_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> tuple[LaminatorCatalog, Session]:
    """Returns laminator catalog and request session for replace routes."""
    return catalog, session


def get_cutter_catalog_and_session(
    catalog: Annotated[CutterCatalog, Depends(get_cutter_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> tuple[CutterCatalog, Session]:
    """Returns cutter catalog and request session for replace routes."""
    return catalog, session


def get_film_catalog_and_session(
    catalog: Annotated[FilmCatalog, Depends(get_film_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> tuple[FilmCatalog, Session]:
    """Returns film catalog and request session for replace routes."""
    return catalog, session


def get_sheet_catalog_and_session(
    catalog: Annotated[SheetCatalog, Depends(get_sheet_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> tuple[SheetCatalog, Session]:
    """Returns sheet catalog and request session for replace routes."""
    return catalog, session


def get_press_operator_catalog_and_session(
    catalog: Annotated[
        PressOperatorCatalog,
        Depends(get_press_operator_catalog),
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> tuple[PressOperatorCatalog, Session]:
    """Returns press operator catalog and session for replace routes."""
    return catalog, session


def get_laminator_operator_catalog_and_session(
    catalog: Annotated[
        LaminatorOperatorCatalog,
        Depends(get_laminator_operator_catalog),
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> tuple[LaminatorOperatorCatalog, Session]:
    """Returns laminator operator catalog and session for replace routes."""
    return catalog, session


def get_cutter_operator_catalog_and_session(
    catalog: Annotated[
        CutterOperatorCatalog,
        Depends(get_cutter_operator_catalog),
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> tuple[CutterOperatorCatalog, Session]:
    """Returns cutter operator catalog and session for replace routes."""
    return catalog, session


def get_die_cut_operator_catalog_and_session(
    catalog: Annotated[
        DieCutterOperatorCatalog,
        Depends(get_die_cut_operator_catalog),
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> tuple[DieCutterOperatorCatalog, Session]:
    """Returns die-cut operator catalog and session for replace routes."""
    return catalog, session


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
