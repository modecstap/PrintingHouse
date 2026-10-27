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
from backend.workplace.order_repository import (
    OrderNotFound,
    OrderStoreUnavailable,
)
from backend.workplace.order_service import WorkplaceOrderService

_T = TypeVar("_T")

router = APIRouter(prefix="/api/v2/reference", tags=["workplace-reference"])


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
def read_reference(
    service: WorkplaceOrderService = Depends(get_workplace_order_service),
) -> WorkplaceOrderBody:
    """Возвращает справочник через reference.

    Результат: HTTP 200 и JSON заказа. Пустое хранилище
    даёт нулевой заказ. Ключа creation_date нет, id равен null.
    Ошибки: HTTP 503, если нет соединения с базой.
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
    """Заменяет справочник через set_reference.

    Результат: HTTP 200 без тела.
    Побочные эффекты: документ справочника заменяется целиком.
    Строка workplace_order не появляется. id тела не выбирает
    заказ. Неверное тело до записи не доходит.
    Ошибки: HTTP 422, если тело не принято. HTTP 500, если
    ставка денег или стоимость операции отрицательная, и
    прежний документ остаётся. HTTP 503, если нет соединения
    с базой.
    """
    _call(lambda: service.set_reference(order_from_body(body)))
    return Response(status_code=200)
