from collections.abc import Callable
from typing import TypeVar

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response

from backend.server.dependencies import (
    get_current_user_with_full_permission,
    get_current_user_with_read_permission,
)
from backend.server.models.workplace_order_body import (
    WorkplaceAcceptedOrderBody,
    WorkplaceCostReportBody,
    WorkplaceOrderBody,
    WorkplaceSavedOrderBody,
    WorkplaceStatusChangeBody,
    body_from_order,
    body_from_report,
    order_from_body,
)
from backend.core.order_repository import (
    OrderNotFound,
    OrderStoreUnavailable,
)
from backend.core.order_service import WorkplaceOrderService

_T = TypeVar("_T")

router = APIRouter(prefix="/api/v2/order", tags=["core-order"])
_service: WorkplaceOrderService | None = None


def bind_workplace_order_service(service: WorkplaceOrderService) -> None:
    """Remembers the workplace order service for the routes.

    :param service:
    """
    global _service
    _service = service


def get_workplace_order_service() -> WorkplaceOrderService:
    """Returns the service that application startup remembered.

    :raises RuntimeError:
    "сервис заказа рабочего места не собран" if bind has not been called yet.

    :return: the WorkplaceOrderService of this process.
    """
    if _service is None:
        raise RuntimeError("сервис заказа рабочего места не собран")
    return _service


def _call(action: Callable[[], _T]) -> _T:
    try:
        return action()
    except OrderNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except OrderStoreUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.get(
    "/",
    dependencies=[Depends(get_current_user_with_read_permission)],
)
def list_orders(
    service: WorkplaceOrderService = Depends(get_workplace_order_service),
) -> list[WorkplaceOrderBody]:
    """Returns workplace orders through take_all.

    :param service:

    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 and a JSON array of orders without reports.
    An empty service result gives [].
    """
    return _call(
        lambda: [body_from_order(order) for order in service.take_all()]
    )


@router.post(
    "/",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def save_order(
    body: WorkplaceOrderBody,
    service: WorkplaceOrderService = Depends(get_workplace_order_service),
) -> WorkplaceSavedOrderBody:
    """Saves a workplace order through save.

    :param body:
    :param service:

    :raises HTTPException: status 404 if the given id does not exist.
    :raises HTTPException: status 422 if the body is not accepted.
    :raises HTTPException: status 500 if a money rate is negative.
    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 and JSON with a single key id.
    """
    saved_id = _call(lambda: service.save(order_from_body(body)))
    return WorkplaceSavedOrderBody(id=saved_id)


@router.post(
    "/cost_report",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def cost_report(
    body: WorkplaceOrderBody,
    service: WorkplaceOrderService = Depends(get_workplace_order_service),
) -> WorkplaceCostReportBody:
    """Calculates the cost through calculate and does not write to the database.

    :param body:
    :param service:

    :raises HTTPException: status 422 if the body is not accepted.
    :raises HTTPException: status 500 if the calculation or a money rate fails.

    :return: HTTP 200 and the CostReport JSON without a wrapper.
    """
    return _call(
        lambda: body_from_report(
            service.calculate(order_from_body(body))
        )
    )


@router.post(
    "/delay",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def delay_order(
    body: WorkplaceOrderBody,
    service: WorkplaceOrderService = Depends(get_workplace_order_service),
) -> WorkplaceAcceptedOrderBody:
    """Delays the order through delay.

    :param body:
    :param service:

    :raises HTTPException: status 404 if the given id does not exist.
    :raises HTTPException: status 422 if the body is not accepted.
    :raises HTTPException: status 500 if the calculation or the rate fails.
    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 and JSON with the id and the cost_report of this calculation.
    """
    saved_id, report = _call(lambda: service.delay(order_from_body(body)))
    return WorkplaceAcceptedOrderBody(
        id=saved_id,
        cost_report=body_from_report(report),
    )


@router.post(
    "/accept",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def accept_order(
    body: WorkplaceOrderBody,
    service: WorkplaceOrderService = Depends(get_workplace_order_service),
) -> WorkplaceAcceptedOrderBody:
    """Accepts the order through accept.

    :param body:
    :param service:

    :raises HTTPException: status 404 if the given id does not exist.
    :raises HTTPException: status 422 if the body is not accepted.
    :raises HTTPException: status 500 if the calculation or the rate fails.
    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 and JSON with the id and the cost_report of this calculation.
    """
    saved_id, report = _call(
        lambda: service.accept(order_from_body(body))
    )
    return WorkplaceAcceptedOrderBody(
        id=saved_id,
        cost_report=body_from_report(report),
    )


@router.post(
    "/status",
    response_model=None,
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def change_status(
    body: WorkplaceStatusChangeBody,
    service: WorkplaceOrderService = Depends(get_workplace_order_service),
) -> Response:
    """Changes the order status through change_status.

    :param body:
    :param service:

    :raises HTTPException: status 404 if the order does not exist.
    :raises HTTPException: status 422 if the body is not accepted.
    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 with no body.
    """
    _call(lambda: service.change_status(body.order_id, body.new_status))
    return Response(status_code=200)


@router.get(
    "/{id}",
    dependencies=[Depends(get_current_user_with_read_permission)],
)
def get_order(
    id: int,
    service: WorkplaceOrderService = Depends(get_workplace_order_service),
) -> WorkplaceOrderBody:
    """Returns the workplace order through take.

    :param id:
    :param service:

    :raises HTTPException: status 404 if the order does not exist.
    :raises HTTPException: status 422 if the path id is not an integer.
    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 and the order JSON without reports.
    """
    return _call(lambda: body_from_order(service.take(id)))


@router.delete(
    "/{id}",
    response_model=None,
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def delete_order(
    id: int,
    service: WorkplaceOrderService = Depends(get_workplace_order_service),
) -> Response:
    """Deletes the workplace order through delete.

    :param id:
    :param service:

    :raises HTTPException: status 404 if the order does not exist.
    :raises HTTPException: status 422 if the path id is not an integer.
    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 with no body.
    """
    _call(lambda: service.delete(id))
    return Response(status_code=200)
