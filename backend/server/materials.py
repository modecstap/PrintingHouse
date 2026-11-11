"""Protected materials catalog HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.new_core.application_services.materials import MaterialCatalogService
from backend.new_core.materials.film import FilmID
from backend.new_core.materials.sheet import SheetID
from backend.server.catalog_mapping import (
    film_from_write_dto,
    film_replace_from_dto,
    film_to_read_dto,
    sheet_from_write_dto,
    sheet_replace_from_dto,
    sheet_to_read_dto,
)
from backend.server.dependencies import (
    get_db_session,
    get_material_catalog_service,
    require_user,
)
from backend.server.schemas import CreatedIdDto, FilmDto, FilmReadDto, SheetDto, SheetReadDto

router = APIRouter(prefix="/api/materials", tags=["materials"])


@router.get("/films", response_model=list[FilmReadDto])
def list_films(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[MaterialCatalogService, Depends(get_material_catalog_service)],
) -> list[FilmReadDto]:
    """Returns every stored film."""
    return [film_to_read_dto(row) for row in service.films()]


@router.get("/films/{film_id}", response_model=FilmReadDto)
def get_film(
    film_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[MaterialCatalogService, Depends(get_material_catalog_service)],
) -> FilmReadDto:
    """Returns one film by id."""
    return film_to_read_dto(service.film(FilmID(film_id)))


@router.post("/films", response_model=CreatedIdDto)
def create_film(
    body: FilmDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[MaterialCatalogService, Depends(get_material_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new film and returns its assigned id."""
    name, price, density = film_from_write_dto(body)
    new_id = service.create_film(name, price, density)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/films/{film_id}", status_code=204, response_class=Response)
def replace_film(
    film_id: int,
    body: FilmDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[MaterialCatalogService, Depends(get_material_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Replaces non-id fields of an existing film."""
    service.replace_film(film_replace_from_dto(film_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/films/{film_id}", status_code=204, response_class=Response)
def delete_film(
    film_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[MaterialCatalogService, Depends(get_material_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a film."""
    service.delete_film(FilmID(film_id))
    session.commit()
    return Response(status_code=204)


@router.get("/paper-types", response_model=list[str])
def list_paper_types(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[MaterialCatalogService, Depends(get_material_catalog_service)],
) -> list[str]:
    """Returns unique paper type names across stored sheets."""
    return list(service.paper_types())


@router.get("/sheets", response_model=list[SheetReadDto])
def list_sheets(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[MaterialCatalogService, Depends(get_material_catalog_service)],
) -> list[SheetReadDto]:
    """Returns every stored sheet."""
    return [sheet_to_read_dto(row) for row in service.sheets()]


@router.get("/sheets/{sheet_id}", response_model=SheetReadDto)
def get_sheet(
    sheet_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[MaterialCatalogService, Depends(get_material_catalog_service)],
) -> SheetReadDto:
    """Returns one sheet by id."""
    return sheet_to_read_dto(service.sheet(SheetID(sheet_id)))


@router.post("/sheets", response_model=CreatedIdDto)
def create_sheet(
    body: SheetDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[MaterialCatalogService, Depends(get_material_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new sheet and returns its assigned id."""
    paper, format = sheet_from_write_dto(body)
    new_id = service.create_sheet(paper, format)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/sheets/{sheet_id}", status_code=204, response_class=Response)
def replace_sheet(
    sheet_id: int,
    body: SheetDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[MaterialCatalogService, Depends(get_material_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Replaces non-id fields of an existing sheet."""
    service.replace_sheet(sheet_replace_from_dto(sheet_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/sheets/{sheet_id}", status_code=204, response_class=Response)
def delete_sheet(
    sheet_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[MaterialCatalogService, Depends(get_material_catalog_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Removes a sheet."""
    service.delete_sheet(SheetID(sheet_id))
    session.commit()
    return Response(status_code=204)
