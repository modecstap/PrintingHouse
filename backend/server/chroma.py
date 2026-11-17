"""Protected chroma catalog HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.new_core.application_services.chroma.catalog import ChromaCatalog
from backend.new_core.chroma import ChromaID
from backend.server.catalog_mapping import (
    chroma_from_write_dto,
    chroma_replace_from_dto,
    chroma_to_read_dto,
)
from backend.server.dependencies import (
    get_chroma_catalog,
    get_chroma_catalog_and_session,
    get_db_session,
    require_user,
)
from backend.server.schemas import ChromaDto, ChromaReadDto, CreatedIdDto

__all__ = [
    "list_chroma",
    "get_chroma",
    "create_chroma",
    "replace_chroma",
    "delete_chroma",
]

router = APIRouter(prefix="/api/chroma", tags=["chroma"])


@router.get("", response_model=list[ChromaReadDto])
def list_chroma(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[ChromaCatalog, Depends(get_chroma_catalog)],
) -> list[ChromaReadDto]:
    """Returns every stored chroma row with a non-empty name.

    :param service: the service.

    :return: the list[ChromaReadDto] result.
    """
    return [chroma_to_read_dto(row) for row in service.chroma_rows()]


@router.get("/{chroma_id}", response_model=ChromaReadDto)
def get_chroma(
    chroma_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[ChromaCatalog, Depends(get_chroma_catalog)],
) -> ChromaReadDto:
    """Returns one chroma row by id.

    :param chroma_id: id of the chroma row.
    :param service: the service.

    :return: the ChromaReadDto result.
    """
    return chroma_to_read_dto(service.chroma_row(ChromaID(chroma_id)))


@router.post("", response_model=CreatedIdDto)
def create_chroma(
    body: ChromaDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[ChromaCatalog, Depends(get_chroma_catalog)],
    session: Annotated[Session, Depends(get_db_session)],
) -> CreatedIdDto:
    """Inserts a new chroma row and returns its assigned id.

    :param body: request body payload.
    :param service: the service.
    :param session: database session.

    :return: the CreatedIdDto result.
    """
    name, cyan, magenta, yellow, black = chroma_from_write_dto(body)
    new_id = service.create_chroma(name, cyan, magenta, yellow, black)
    session.commit()
    return CreatedIdDto(id=new_id.value)


@router.put("/{chroma_id}", status_code=204, response_class=Response)
def replace_chroma(
    chroma_id: int,
    body: ChromaDto,
    _user: Annotated[str, Depends(require_user)],
    deps: Annotated[
        tuple[ChromaCatalog, Session],
        Depends(get_chroma_catalog_and_session),
    ],
) -> Response:
    """Replaces non-id fields of an existing chroma row.

    :param chroma_id: id of the chroma row.
    :param body: request body payload.
    :param deps: catalog service and session.

    :return: the Response result.
    """
    catalog, session = deps
    catalog.replace_chroma(chroma_replace_from_dto(chroma_id, body))
    session.commit()
    return Response(status_code=204)


@router.delete("/{chroma_id}", status_code=204, response_class=Response)
def delete_chroma(
    chroma_id: int,
    _user: Annotated[str, Depends(require_user)],
    deps: Annotated[
        tuple[ChromaCatalog, Session],
        Depends(get_chroma_catalog_and_session),
    ],
) -> Response:
    """Removes a chroma row.

    :param chroma_id: id of the chroma row.
    :param deps: catalog service and session.

    :return: the Response result.
    """
    catalog, session = deps
    catalog.delete_chroma(ChromaID(chroma_id))
    session.commit()
    return Response(status_code=204)