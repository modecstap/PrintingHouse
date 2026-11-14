"""Protected equipment catalog HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from backend.new_core.application_services.equipment import EquipmentCatalogService
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
    get_db_session,
    get_equipment_catalog_service,
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

router = APIRouter(prefix="/api/equipment", tags=["equipment"])


def _require_body_id_matches_path(path_id: int, body_id: int) -> None:
    if body_id != path_id:
        raise HTTPException(
            status_code=400,
            detail="id в теле запроса должен совпадать с id в пути",
        )


@router.get("/printers", response_model=list[PrinterDto])
def list_printers(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
) -> list[PrinterDto]:
    """Returns every stored printer."""
    return [printer_to_dto(row) for row in service.printers()]


@router.get("/printers/{printer_id}", response_model=PrinterDto)
def get_printer(
    printer_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
) -> PrinterDto:
    """Returns one printer by id."""
    return printer_to_dto(service.printer(PrinterID(printer_id)))


@router.post("/printers", response_model=CreatedIdDto)
def create_printer(
    body: PrinterWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new printer and returns its assigned id."""
    (
        name,
        spacing,
        startup,
        cyan,
        magenta,
        yellow,
        black,
    ) = printer_from_write_dto(body)
    new_id = service.create_printer(
        name,
        spacing,
        startup,
        cyan,
        magenta,
        yellow,
        black,
    )
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/printers/{printer_id}", status_code=204, response_class=Response)
def replace_printer(
    printer_id: int,
    body: PrinterDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Replaces non-id fields of an existing printer."""
    _require_body_id_matches_path(printer_id, body.id)
    service.replace_printer(printer_replace_from_dto(printer_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/printers/{printer_id}", status_code=204, response_class=Response)
def delete_printer(
    printer_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a printer."""
    service.delete_printer(PrinterID(printer_id))
    session.commit()
    return Response(status_code=204)


@router.get("/laminators", response_model=list[LaminatorDto])
def list_laminators(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
) -> list[LaminatorDto]:
    """Returns every stored laminator."""
    return [laminator_to_dto(row) for row in service.laminators()]


@router.get("/laminators/{laminator_id}", response_model=LaminatorDto)
def get_laminator(
    laminator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
) -> LaminatorDto:
    """Returns one laminator by id."""
    return laminator_to_dto(service.laminator(LaminatorID(laminator_id)))


@router.post("/laminators", response_model=CreatedIdDto)
def create_laminator(
    body: LaminatorWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new laminator and returns its assigned id."""
    name, startup = laminator_from_write_dto(body)
    new_id = service.create_laminator(name, startup)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/laminators/{laminator_id}", status_code=204, response_class=Response)
def replace_laminator(
    laminator_id: int,
    body: LaminatorDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Replaces non-id fields of an existing laminator."""
    _require_body_id_matches_path(laminator_id, body.id)
    service.replace_laminator(laminator_replace_from_dto(laminator_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/laminators/{laminator_id}", status_code=204, response_class=Response)
def delete_laminator(
    laminator_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a laminator."""
    service.delete_laminator(LaminatorID(laminator_id))
    session.commit()
    return Response(status_code=204)


@router.get("/cutters", response_model=list[CutterDto])
def list_cutters(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
) -> list[CutterDto]:
    """Returns every stored cutter."""
    return [cutter_to_dto(row) for row in service.cutters()]


@router.get("/cutters/{cutter_id}", response_model=CutterDto)
def get_cutter(
    cutter_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
) -> CutterDto:
    """Returns one cutter by id."""
    return cutter_to_dto(service.cutter(CutterID(cutter_id)))


@router.post("/cutters", response_model=CreatedIdDto)
def create_cutter(
    body: CutterWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new cutter and returns its assigned id."""
    name, max_stack = cutter_from_write_dto(body)
    new_id = service.create_cutter(name, max_stack)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/cutters/{cutter_id}", status_code=204, response_class=Response)
def replace_cutter(
    cutter_id: int,
    body: CutterDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Replaces non-id fields of an existing cutter."""
    _require_body_id_matches_path(cutter_id, body.id)
    service.replace_cutter(cutter_replace_from_dto(cutter_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/cutters/{cutter_id}", status_code=204, response_class=Response)
def delete_cutter(
    cutter_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a cutter."""
    service.delete_cutter(CutterID(cutter_id))
    session.commit()
    return Response(status_code=204)
