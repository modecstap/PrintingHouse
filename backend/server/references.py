"""Protected reference HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.new_core.application_services.reference import (
    ReferenceOrderService,
)
from backend.server.dependencies import (
    get_db_session,
    get_reference_service,
    require_user,
)
from backend.server.mapping import (
    order_to_dto,
    reference_from_dto,
    reference_to_dto,
)
from backend.server.schemas import OrderDto, ReferenceDto

__all__ = [
    "list_references",
    "list_reference_orders",
    "save_reference",
]

router = APIRouter(prefix="/api/references", tags=["references"])


@router.get("", response_model=list[ReferenceDto])
def list_references(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[ReferenceOrderService, Depends(get_reference_service)],
) -> list[ReferenceDto]:
    """Returns every stored reference.

    :param service: the service.

    :return: the list[ReferenceDto] result.
    """
    return [reference_to_dto(row) for row in service.references()]


@router.get("/orders", response_model=list[OrderDto])
def list_reference_orders(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[ReferenceOrderService, Depends(get_reference_service)],
) -> list[OrderDto]:
    """Returns orders linked to references.

    :param service: the service.

    :return: the list[OrderDto] result.
    """
    return [order_to_dto(order) for order in service.reference_orders()]


@router.post("", status_code=204, response_class=Response)
def save_reference(
    body: ReferenceDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[ReferenceOrderService, Depends(get_reference_service)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Stores a new reference row.

    :param body: request body payload.
    :param service: the service.
    :param session: database session.

    :return: the Response result.
    """
    service.save(reference_from_dto(body))
    session.commit()
    return Response(status_code=204)
