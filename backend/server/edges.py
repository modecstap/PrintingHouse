"""Protected edges catalog HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.new_core.application_services.edges.catalog import EdgesCatalog
from backend.new_core.edges import EdgesID
from backend.server.catalog_mapping import (
    edges_from_write_dto,
    edges_replace_from_dto,
    edges_to_read_dto,
)
from backend.server.dependencies import (
    get_db_session,
    get_edges_catalog,
    get_edges_catalog_and_session,
    require_user,
)
from backend.server.schemas import CreatedIdDto, EdgesDto, EdgesReadDto

__all__ = [
    "list_edges",
    "get_edges",
    "create_edges",
    "replace_edges",
    "delete_edges",
]

router = APIRouter(prefix="/api/edges", tags=["edges"])


@router.get("", response_model=list[EdgesReadDto])
def list_edges(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EdgesCatalog, Depends(get_edges_catalog)],
) -> list[EdgesReadDto]:
    """Returns every stored edges row.

    :param service: the service.

    :return: the list[EdgesReadDto] result.
    """
    return [edges_to_read_dto(row) for row in service.edges_rows()]


@router.get("/{edges_id}", response_model=EdgesReadDto)
def get_edges(
    edges_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EdgesCatalog, Depends(get_edges_catalog)],
) -> EdgesReadDto:
    """Returns one edges row by id.

    :param edges_id: id of the edges row.
    :param service: the service.

    :return: the EdgesReadDto result.
    """
    return edges_to_read_dto(service.edges_row(EdgesID(edges_id)))


@router.post("", response_model=CreatedIdDto)
def create_edges(
    body: EdgesDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[EdgesCatalog, Depends(get_edges_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new edges row and returns its assigned id.

    :param body: request body payload.
    :param service: the service.
    :param session: database session.

    :return: the CreatedIdDto result.
    """
    name, bleeds, spacing = edges_from_write_dto(body)
    new_id = service.create_edges(name, bleeds, spacing)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/{edges_id}", status_code=204, response_class=Response)
def replace_edges(
    edges_id: int,
    body: EdgesDto,
    _user: Annotated[str, Depends(require_user)],
    deps: Annotated[
        tuple[EdgesCatalog, Session],
        Depends(get_edges_catalog_and_session),
    ],
) -> Response:
    """Replaces non-id fields of an existing edges row.

    :param edges_id: id of the edges row.
    :param body: request body payload.
    :param deps: catalog service and session.

    :return: the Response result.
    """
    catalog, session = deps
    catalog.replace_edges(edges_replace_from_dto(edges_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/{edges_id}", status_code=204, response_class=Response)
def delete_edges(
    edges_id: int,
    _user: Annotated[str, Depends(require_user)],
    deps: Annotated[
        tuple[EdgesCatalog, Session],
        Depends(get_edges_catalog_and_session),
    ],
) -> Response:
    """Removes an edges row.

    :param edges_id: id of the edges row.
    :param deps: catalog service and session.

    :return: the Response result.
    """
    catalog, session = deps
    catalog.delete_edges(EdgesID(edges_id))
    session.commit()
    return Response(status_code=204)