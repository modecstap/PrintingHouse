"""Protected equipment catalog HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.new_core.application_services.equipment import EquipmentCatalogService
from backend.new_core.equipment.cutter import CutterID
from backend.new_core.equipment.laminator import LaminatorID
from backend.new_core.equipment.printer import PrinterID
from backend.server.catalog_mapping import (
    cutter_from_dto,
    cutter_to_dto,
    laminator_from_dto,
    laminator_to_dto,
    printer_from_dto,
    printer_to_dto,
)
from backend.server.dependencies import (
    get_db_session,
    get_equipment_catalog_service,
    require_user,
)
from backend.server.schemas import CutterDto, LaminatorDto, PrinterDto

router = APIRouter(prefix="/api/equipment", tags=["equipment"])


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


@router.post("/printers", status_code=204, response_class=Response)
def save_printer(
    body: PrinterDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Stores a new printer."""
    service.save_printer(printer_from_dto(body))
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


@router.post("/laminators", status_code=204, response_class=Response)
def save_laminator(
    body: LaminatorDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Stores a new laminator."""
    service.save_laminator(laminator_from_dto(body))
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


@router.post("/cutters", status_code=204, response_class=Response)
def save_cutter(
    body: CutterDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EquipmentCatalogService, Depends(get_equipment_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Stores a new cutter."""
    service.save_cutter(cutter_from_dto(body))
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
