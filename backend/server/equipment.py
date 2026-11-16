"""Protected equipment catalog HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from backend.new_core.application_services.equipment.cutters import (
    CutterCatalog,
)
from backend.new_core.application_services.equipment.laminators import (
    LaminatorCatalog,
)
from backend.new_core.application_services.equipment.printers import (
    PrinterCatalog,
)
from backend.new_core.equipment.cutter import CutterID
from backend.new_core.equipment.laminator import LaminatorID
from backend.new_core.equipment.printer import PrinterID
from backend.server.catalog_mapping import (
    cutter_from_write_dto,
    cutter_replace_from_dto,
    cutter_to_dto,
    laminator_from_write_dto,
    laminator_replace_from_dto,
    laminator_to_dto,
    printer_from_write_dto,
    printer_replace_from_dto,
    printer_to_dto,
)
from backend.server.dependencies import (
    get_cutter_catalog,
    get_cutter_catalog_and_session,
    get_db_session,
    get_laminator_catalog,
    get_laminator_catalog_and_session,
    get_printer_catalog,
    get_printer_catalog_and_session,
    require_user,
)
from backend.server.schemas import (
    CreatedIdDto,
    CutterDto,
    CutterWriteDto,
    LaminatorDto,
    LaminatorWriteDto,
    PrinterDto,
    PrinterWriteDto,
)

__all__ = [
    "list_printers",
    "get_printer",
    "create_printer",
    "replace_printer",
    "delete_printer",
    "list_laminators",
    "get_laminator",
    "create_laminator",
    "replace_laminator",
    "delete_laminator",
    "list_cutters",
    "get_cutter",
    "create_cutter",
    "replace_cutter",
    "delete_cutter",
]

router = APIRouter(prefix="/api/equipment", tags=["equipment"])


def _require_body_id_matches_path(path_id: int, body_id: int) -> None:
    """Handles require body id matches path.

    :param path_id: id of the path.
    :param body_id: id of the body.

    :raises HTTPException: when the operation fails.
    """
    if body_id != path_id:
        raise HTTPException(
            status_code=400,
            detail="id в теле запроса должен совпадать с id в пути",
        )


@router.get("/printers", response_model=list[PrinterDto])
def list_printers(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[PrinterCatalog, Depends(get_printer_catalog)],
) -> list[PrinterDto]:
    """Returns every stored printer.

    :param service: the service.

    :return: the list[PrinterDto] result.
    """
    return [printer_to_dto(row) for row in service.printers()]


@router.get("/printers/{printer_id}", response_model=PrinterDto)
def get_printer(
    printer_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[PrinterCatalog, Depends(get_printer_catalog)],
) -> PrinterDto:
    """Returns one printer by id.

    :param printer_id: id of the printer.
    :param service: the service.

    :return: the PrinterDto result.
    """
    return printer_to_dto(service.printer(PrinterID(printer_id)))


@router.post("/printers", response_model=CreatedIdDto)
def create_printer(
    body: PrinterWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[PrinterCatalog, Depends(get_printer_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new printer and returns its assigned id.

    :param body: request body payload.
    :param service: the service.
    :param session: database session.

    :return: the CreatedIdDto result.
    """
    name, spacing, prices = printer_from_write_dto(body)
    new_id = service.create_printer(name, spacing, prices)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/printers/{printer_id}", status_code=204, response_class=Response)
def replace_printer(
    printer_id: int,
    body: PrinterDto,
    _user: Annotated[str, Depends(require_user)],
    deps: Annotated[
        tuple[PrinterCatalog, Session],
        Depends(get_printer_catalog_and_session),
    ],
) -> Response:
    """Replaces non-id fields of an existing printer.

    :param printer_id: id of the printer.
    :param body: request body payload.
    :param deps: the deps.

    :return: the Response result.
    """
    service, session = deps
    _require_body_id_matches_path(printer_id, body.id)
    service.replace_printer(printer_replace_from_dto(printer_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/printers/{printer_id}",
               status_code=204, response_class=Response)
def delete_printer(
    printer_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[PrinterCatalog, Depends(get_printer_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a printer.

    :param printer_id: id of the printer.
    :param service: the service.
    :param session: database session.

    :return: the Response result.
    """
    service.delete_printer(PrinterID(printer_id))
    session.commit()
    return Response(status_code=204)


@router.get("/laminators", response_model=list[LaminatorDto])
def list_laminators(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[LaminatorCatalog, Depends(get_laminator_catalog)],
) -> list[LaminatorDto]:
    """Returns every stored laminator.

    :param service: the service.

    :return: the list[LaminatorDto] result.
    """
    return [laminator_to_dto(row) for row in service.laminators()]


@router.get("/laminators/{laminator_id}", response_model=LaminatorDto)
def get_laminator(
    laminator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[LaminatorCatalog, Depends(get_laminator_catalog)],
) -> LaminatorDto:
    """Returns one laminator by id.

    :param laminator_id: id of the laminator.
    :param service: the service.

    :return: the LaminatorDto result.
    """
    return laminator_to_dto(service.laminator(LaminatorID(laminator_id)))


@router.post("/laminators", response_model=CreatedIdDto)
def create_laminator(
    body: LaminatorWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[LaminatorCatalog, Depends(get_laminator_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new laminator and returns its assigned id.

    :param body: request body payload.
    :param service: the service.
    :param session: database session.

    :return: the CreatedIdDto result.
    """
    name, startup = laminator_from_write_dto(body)
    new_id = service.create_laminator(name, startup)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/laminators/{laminator_id}",
            status_code=204, response_class=Response)
def replace_laminator(
    laminator_id: int,
    body: LaminatorDto,
    _user: Annotated[str, Depends(require_user)],
    deps: Annotated[
        tuple[LaminatorCatalog, Session],
        Depends(get_laminator_catalog_and_session),
    ],
) -> Response:
    """Replaces non-id fields of an existing laminator.

    :param laminator_id: id of the laminator.
    :param body: request body payload.
    :param deps: the deps.

    :return: the Response result.
    """
    service, session = deps
    _require_body_id_matches_path(laminator_id, body.id)
    service.replace_laminator(laminator_replace_from_dto(laminator_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/laminators/{laminator_id}",
               status_code=204, response_class=Response)
def delete_laminator(
    laminator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[LaminatorCatalog, Depends(get_laminator_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a laminator.

    :param laminator_id: id of the laminator.
    :param service: the service.
    :param session: database session.

    :return: the Response result.
    """
    service.delete_laminator(LaminatorID(laminator_id))
    session.commit()
    return Response(status_code=204)


@router.get("/cutters", response_model=list[CutterDto])
def list_cutters(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[CutterCatalog, Depends(get_cutter_catalog)],
) -> list[CutterDto]:
    """Returns every stored cutter.

    :param service: the service.

    :return: the list[CutterDto] result.
    """
    return [cutter_to_dto(row) for row in service.cutters()]


@router.get("/cutters/{cutter_id}", response_model=CutterDto)
def get_cutter(
    cutter_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[CutterCatalog, Depends(get_cutter_catalog)],
) -> CutterDto:
    """Returns one cutter by id.

    :param cutter_id: id of the cutter.
    :param service: the service.

    :return: the CutterDto result.
    """
    return cutter_to_dto(service.cutter(CutterID(cutter_id)))


@router.post("/cutters", response_model=CreatedIdDto)
def create_cutter(
    body: CutterWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[CutterCatalog, Depends(get_cutter_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new cutter and returns its assigned id.

    :param body: request body payload.
    :param service: the service.
    :param session: database session.

    :return: the CreatedIdDto result.
    """
    name, max_stack = cutter_from_write_dto(body)
    new_id = service.create_cutter(name, max_stack)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/cutters/{cutter_id}", status_code=204, response_class=Response)
def replace_cutter(
    cutter_id: int,
    body: CutterDto,
    _user: Annotated[str, Depends(require_user)],
    deps: Annotated[
        tuple[CutterCatalog, Session],
        Depends(get_cutter_catalog_and_session),
    ],
) -> Response:
    """Replaces non-id fields of an existing cutter.

    :param cutter_id: id of the cutter.
    :param body: request body payload.
    :param deps: the deps.

    :return: the Response result.
    """
    service, session = deps
    _require_body_id_matches_path(cutter_id, body.id)
    service.replace_cutter(cutter_replace_from_dto(cutter_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/cutters/{cutter_id}", status_code=204, response_class=Response)
def delete_cutter(
    cutter_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[CutterCatalog, Depends(get_cutter_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a cutter.

    :param cutter_id: id of the cutter.
    :param service: the service.
    :param session: database session.

    :return: the Response result.
    """
    service.delete_cutter(CutterID(cutter_id))
    session.commit()
    return Response(status_code=204)
