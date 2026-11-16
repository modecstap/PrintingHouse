"""Protected staff catalog HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

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
from backend.new_core.personal.cutter_operator import CutterOperatorID
from backend.new_core.personal.die_cutter_operator import DieCutterOperatorID
from backend.new_core.personal.laminator_operator import LaminatorOperatorID
from backend.new_core.personal.press_operator import PressOperatorID
from backend.server.catalog_mapping import (
    cutter_operator_replace_from_dto,
    die_cut_operator_replace_from_dto,
    laminator_operator_replace_from_dto,
    operator_from_write_dto,
    operator_to_dto,
    press_operator_replace_from_dto,
)
from backend.server.dependencies import (
    get_cutter_operator_catalog,
    get_cutter_operator_catalog_and_session,
    get_db_session,
    get_die_cut_operator_catalog,
    get_die_cut_operator_catalog_and_session,
    get_laminator_operator_catalog,
    get_laminator_operator_catalog_and_session,
    get_press_operator_catalog,
    get_press_operator_catalog_and_session,
    require_user,
)
from backend.server.schemas import CreatedIdDto, OperatorDto, OperatorWriteDto

router = APIRouter(prefix="/api/staff", tags=["staff"])


def _require_body_id_matches_path(path_id: int, body_id: int) -> None:
    if body_id != path_id:
        raise HTTPException(
            status_code=400,
            detail="id в теле запроса должен совпадать с id в пути",
        )


@router.get("/press-operators", response_model=list[OperatorDto])
def list_press_operators(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[PressOperatorCatalog, Depends(get_press_operator_catalog)],
) -> list[OperatorDto]:
    """Returns every press operator."""
    return [operator_to_dto(row) for row in service.press_operators()]


@router.get("/press-operators/{operator_id}", response_model=OperatorDto)
def get_press_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[PressOperatorCatalog, Depends(get_press_operator_catalog)],
) -> OperatorDto:
    """Returns one press operator by id."""
    return operator_to_dto(service.press_operator(PressOperatorID(operator_id)))


@router.post("/press-operators", response_model=CreatedIdDto)
def create_press_operator(
    body: OperatorWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[PressOperatorCatalog, Depends(get_press_operator_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new press operator and returns its assigned id."""
    name, salary = operator_from_write_dto(body)
    new_id = service.create_press_operator(name, salary)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/press-operators/{operator_id}", status_code=204, response_class=Response)
def replace_press_operator(
    operator_id: int,
    body: OperatorDto,
    _user: Annotated[str, Depends(require_user)],
    deps: Annotated[
        tuple[PressOperatorCatalog, Session],
        Depends(get_press_operator_catalog_and_session),
    ],
) -> Response:
    """Replaces non-id fields of an existing press operator."""
    service, session = deps
    _require_body_id_matches_path(operator_id, body.id)
    service.replace_press_operator(press_operator_replace_from_dto(operator_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/press-operators/{operator_id}", status_code=204, response_class=Response)
def delete_press_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[PressOperatorCatalog, Depends(get_press_operator_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a press operator."""
    service.delete_press_operator(PressOperatorID(operator_id))
    session.commit()
    return Response(status_code=204)


@router.get("/laminator-operators", response_model=list[OperatorDto])
def list_laminator_operators(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[
        LaminatorOperatorCatalog,
        Depends(get_laminator_operator_catalog),
    ],
) -> list[OperatorDto]:
    """Returns every laminator operator."""
    return [operator_to_dto(row) for row in service.laminator_operators()]


@router.get("/laminator-operators/{operator_id}", response_model=OperatorDto)
def get_laminator_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[
        LaminatorOperatorCatalog,
        Depends(get_laminator_operator_catalog),
    ],
) -> OperatorDto:
    """Returns one laminator operator by id."""
    return operator_to_dto(
        service.laminator_operator(LaminatorOperatorID(operator_id)),
    )


@router.post("/laminator-operators", response_model=CreatedIdDto)
def create_laminator_operator(
    body: OperatorWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[
        LaminatorOperatorCatalog,
        Depends(get_laminator_operator_catalog),
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new laminator operator and returns its assigned id."""
    name, salary = operator_from_write_dto(body)
    new_id = service.create_laminator_operator(name, salary)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put(
    "/laminator-operators/{operator_id}",
    status_code=204,
    response_class=Response,
)
def replace_laminator_operator(
    operator_id: int,
    body: OperatorDto,
    _user: Annotated[str, Depends(require_user)],
    deps: Annotated[
        tuple[LaminatorOperatorCatalog, Session],
        Depends(get_laminator_operator_catalog_and_session),
    ],
) -> Response:
    """Replaces non-id fields of an existing laminator operator."""
    service, session = deps
    _require_body_id_matches_path(operator_id, body.id)
    service.replace_laminator_operator(
        laminator_operator_replace_from_dto(operator_id, body),
    )
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
    service: Annotated[
        LaminatorOperatorCatalog,
        Depends(get_laminator_operator_catalog),
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a laminator operator."""
    service.delete_laminator_operator(LaminatorOperatorID(operator_id))
    session.commit()
    return Response(status_code=204)


@router.get("/cutter-operators", response_model=list[OperatorDto])
def list_cutter_operators(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[CutterOperatorCatalog, Depends(get_cutter_operator_catalog)],
) -> list[OperatorDto]:
    """Returns every cutter operator."""
    return [operator_to_dto(row) for row in service.cutter_operators()]


@router.get("/cutter-operators/{operator_id}", response_model=OperatorDto)
def get_cutter_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[CutterOperatorCatalog, Depends(get_cutter_operator_catalog)],
) -> OperatorDto:
    """Returns one cutter operator by id."""
    return operator_to_dto(service.cutter_operator(CutterOperatorID(operator_id)))


@router.post("/cutter-operators", response_model=CreatedIdDto)
def create_cutter_operator(
    body: OperatorWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[CutterOperatorCatalog, Depends(get_cutter_operator_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new cutter operator and returns its assigned id."""
    name, salary = operator_from_write_dto(body)
    new_id = service.create_cutter_operator(name, salary)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/cutter-operators/{operator_id}", status_code=204, response_class=Response)
def replace_cutter_operator(
    operator_id: int,
    body: OperatorDto,
    _user: Annotated[str, Depends(require_user)],
    deps: Annotated[
        tuple[CutterOperatorCatalog, Session],
        Depends(get_cutter_operator_catalog_and_session),
    ],
) -> Response:
    """Replaces non-id fields of an existing cutter operator."""
    service, session = deps
    _require_body_id_matches_path(operator_id, body.id)
    service.replace_cutter_operator(cutter_operator_replace_from_dto(operator_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/cutter-operators/{operator_id}", status_code=204, response_class=Response)
def delete_cutter_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[CutterOperatorCatalog, Depends(get_cutter_operator_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a cutter operator."""
    service.delete_cutter_operator(CutterOperatorID(operator_id))
    session.commit()
    return Response(status_code=204)


@router.get("/die-cut-operators", response_model=list[OperatorDto])
def list_die_cut_operators(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[
        DieCutterOperatorCatalog,
        Depends(get_die_cut_operator_catalog),
    ],
) -> list[OperatorDto]:
    """Returns every die-cut operator."""
    return [operator_to_dto(row) for row in service.die_cut_operators()]


@router.get("/die-cut-operators/{operator_id}", response_model=OperatorDto)
def get_die_cut_operator(
    operator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[
        DieCutterOperatorCatalog,
        Depends(get_die_cut_operator_catalog),
    ],
) -> OperatorDto:
    """Returns one die-cut operator by id."""
    return operator_to_dto(
        service.die_cut_operator(DieCutterOperatorID(operator_id)),
    )


@router.post("/die-cut-operators", response_model=CreatedIdDto)
def create_die_cut_operator(
    body: OperatorWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[
        DieCutterOperatorCatalog,
        Depends(get_die_cut_operator_catalog),
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new die-cut operator and returns its assigned id."""
    name, salary = operator_from_write_dto(body)
    new_id = service.create_die_cut_operator(name, salary)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put(
    "/die-cut-operators/{operator_id}",
    status_code=204,
    response_class=Response,
)
def replace_die_cut_operator(
    operator_id: int,
    body: OperatorDto,
    _user: Annotated[str, Depends(require_user)],
    deps: Annotated[
        tuple[DieCutterOperatorCatalog, Session],
        Depends(get_die_cut_operator_catalog_and_session),
    ],
) -> Response:
    """Replaces non-id fields of an existing die-cut operator."""
    service, session = deps
    _require_body_id_matches_path(operator_id, body.id)
    service.replace_die_cut_operator(die_cut_operator_replace_from_dto(operator_id, body))
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
    service: Annotated[
        DieCutterOperatorCatalog,
        Depends(get_die_cut_operator_catalog),
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a die-cut operator."""
    service.delete_die_cut_operator(DieCutterOperatorID(operator_id))
    session.commit()
    return Response(status_code=204)
