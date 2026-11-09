"""Protected staff catalog HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.new_core.application_services.personal import StaffCatalogService
from backend.new_core.personal.cutter_operator import CutterOperatorID
from backend.new_core.personal.die_cutter_operator import DieCutterOperatorID
from backend.new_core.personal.laminator_operator import LaminatorOperatorID
from backend.new_core.personal.press_operator import PressOperatorID
from backend.server.catalog_mapping import (
    cutter_operator_from_dto,
    die_cut_operator_from_dto,
    laminator_operator_from_dto,
    operator_to_dto,
    press_operator_from_dto,
)
from backend.server.dependencies import (
    get_db_session,
    get_staff_catalog_service,
    require_user,
)
from backend.server.schemas import OperatorDto

router = APIRouter(prefix="/api/staff", tags=["staff"])


@router.get("/press-operators", response_model=list[OperatorDto])
def list_press_operators(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
) -> list[OperatorDto]:
    """Returns every press operator."""
    return [operator_to_dto(row) for row in service.press_operators()]


@router.get("/press-operators/{operator_id}", response_model=OperatorDto)
def get_press_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
) -> OperatorDto:
    """Returns one press operator by id."""
    return operator_to_dto(service.press_operator(PressOperatorID(operator_id)))


@router.post("/press-operators", status_code=204, response_class=Response)
def save_press_operator(
    body: OperatorDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Stores a new press operator."""
    service.save_press_operator(press_operator_from_dto(body))
    session.commit()
    return Response(status_code=204)


@router.delete("/press-operators/{operator_id}", status_code=204, response_class=Response)
def delete_press_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a press operator."""
    service.delete_press_operator(PressOperatorID(operator_id))
    session.commit()
    return Response(status_code=204)


@router.get("/laminator-operators", response_model=list[OperatorDto])
def list_laminator_operators(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
) -> list[OperatorDto]:
    """Returns every laminator operator."""
    return [operator_to_dto(row) for row in service.laminator_operators()]


@router.get("/laminator-operators/{operator_id}", response_model=OperatorDto)
def get_laminator_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
) -> OperatorDto:
    """Returns one laminator operator by id."""
    return operator_to_dto(
        service.laminator_operator(LaminatorOperatorID(operator_id)),
    )


@router.post("/laminator-operators", status_code=204, response_class=Response)
def save_laminator_operator(
    body: OperatorDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Stores a new laminator operator."""
    service.save_laminator_operator(laminator_operator_from_dto(body))
    session.commit()
    return Response(status_code=204)


@router.delete(
    "/laminator-operators/{operator_id}",
    status_code=204,
    response_class=Response,
)
def delete_laminator_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a laminator operator."""
    service.delete_laminator_operator(LaminatorOperatorID(operator_id))
    session.commit()
    return Response(status_code=204)


@router.get("/cutter-operators", response_model=list[OperatorDto])
def list_cutter_operators(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
) -> list[OperatorDto]:
    """Returns every cutter operator."""
    return [operator_to_dto(row) for row in service.cutter_operators()]


@router.get("/cutter-operators/{operator_id}", response_model=OperatorDto)
def get_cutter_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
) -> OperatorDto:
    """Returns one cutter operator by id."""
    return operator_to_dto(service.cutter_operator(CutterOperatorID(operator_id)))


@router.post("/cutter-operators", status_code=204, response_class=Response)
def save_cutter_operator(
    body: OperatorDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Stores a new cutter operator."""
    service.save_cutter_operator(cutter_operator_from_dto(body))
    session.commit()
    return Response(status_code=204)


@router.delete("/cutter-operators/{operator_id}", status_code=204, response_class=Response)
def delete_cutter_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a cutter operator."""
    service.delete_cutter_operator(CutterOperatorID(operator_id))
    session.commit()
    return Response(status_code=204)


@router.get("/die-cut-operators", response_model=list[OperatorDto])
def list_die_cut_operators(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
) -> list[OperatorDto]:
    """Returns every die-cut operator."""
    return [operator_to_dto(row) for row in service.die_cut_operators()]


@router.get("/die-cut-operators/{operator_id}", response_model=OperatorDto)
def get_die_cut_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
) -> OperatorDto:
    """Returns one die-cut operator by id."""
    return operator_to_dto(
        service.die_cut_operator(DieCutterOperatorID(operator_id)),
    )


@router.post("/die-cut-operators", status_code=204, response_class=Response)
def save_die_cut_operator(
    body: OperatorDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Stores a new die-cut operator."""
    service.save_die_cut_operator(die_cut_operator_from_dto(body))
    session.commit()
    return Response(status_code=204)


@router.delete(
    "/die-cut-operators/{operator_id}",
    status_code=204,
    response_class=Response,
)
def delete_die_cut_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[StaffCatalogService, Depends(get_staff_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a die-cut operator."""
    service.delete_die_cut_operator(DieCutterOperatorID(operator_id))
    session.commit()
    return Response(status_code=204)
