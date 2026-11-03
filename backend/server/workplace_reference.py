from collections.abc import Callable
from typing import TypeVar

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response

from backend.server.dependencies import (
    get_current_user_with_full_permission,
    get_current_user_with_read_permission,
)
from backend.server.models.workplace_order_body import (
    WorkplaceOrderBody,
    body_from_order,
    order_from_body,
)
from backend.server.workplace_order import get_workplace_order_service
from backend.core.order_repository import (
    OrderNotFound,
    OrderStoreUnavailable,
)
from backend.core.order_service import WorkplaceOrderService
from backend.core.sheet.repository import (
    SheetIdEmpty,
    SheetNotFound,
    SheetStoreUnavailable,
)

_T = TypeVar("_T")

router = APIRouter(prefix="/api/v2/reference", tags=["core-reference"])


def _call(action: Callable[[], _T]) -> _T:
    try:
        return action()
    except SheetIdEmpty as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except (OrderNotFound, SheetNotFound) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OrderStoreUnavailable, SheetStoreUnavailable) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.get(
    "/",
    dependencies=[Depends(get_current_user_with_read_permission)],
)
def read_reference(
    service: WorkplaceOrderService = Depends(get_workplace_order_service),
) -> WorkplaceOrderBody:
    """Returns the reference through reference.

    :param service:

    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 and the order JSON. An empty store gives an empty order.
    There is no creation_date key, and id is null.
    """
    return _call(lambda: body_from_order(service.reference()))


@router.post(
    "/",
    response_model=None,
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def replace_reference(
    body: WorkplaceOrderBody,
    service: WorkplaceOrderService = Depends(get_workplace_order_service),
) -> Response:
    """Replaces the reference through set_reference.

    :param body:
    :param service:

    :raises HTTPException: status 404 if a printing names a sheet id
    that has no row. The reference is not replaced.
    :raises HTTPException: status 422 if the body is not accepted
    or a printing has no sheet id.
    :raises HTTPException: status 500 if a money rate or an operation cost is negative.
    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 with no body.
    """
    _call(lambda: service.set_reference(order_from_body(body)))
    return Response(status_code=200)
