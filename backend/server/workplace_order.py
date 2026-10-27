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
from backend.workplace.order_repository import (
    OrderNotFound,
    OrderStoreUnavailable,
)
from backend.workplace.order_service import WorkplaceOrderService

_T = TypeVar("_T")

router = APIRouter(prefix="/api/v2/order", tags=["workplace-order"])
_service: WorkplaceOrderService | None = None


def bind_workplace_order_service(service: WorkplaceOrderService) -> None:
    """Запоминает сервис заказа рабочего места для маршрутов.

    Побочные эффекты: следующий get_workplace_order_service
    возвращает этот сервис. Engine не создаёт.
    """
    global _service
    _service = service


def get_workplace_order_service() -> WorkplaceOrderService:
    """Возвращает сервис, который запомнила сборка приложения.

    Результат: WorkplaceOrderService этого процесса.
    Ошибки: RuntimeError «сервис заказа рабочего места не собран»,
    если bind ещё не вызывали.
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
    """Возвращает заказы рабочего места через take_all.

    Результат: HTTP 200 и JSON-массив заказов без отчётов.
    Пустой результат сервиса даёт [].
    Ошибки: HTTP 503, если нет соединения с базой.
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
    """Сохраняет заказ рабочего места через save.

    Результат: HTTP 200 и JSON с одним ключом id.
    Побочные эффекты: новая строка или обновление существующей.
    Отчёт не пишется.
    Ошибки: HTTP 404, если заданного id нет. HTTP 422, если тело
    не принято. HTTP 500, если ставка денег отрицательная.
    HTTP 503, если нет соединения с базой.
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
    """Считает стоимость через calculate и в базу не пишет.

    Результат: HTTP 200 и JSON CostReport без обёртки.
    Ошибки: HTTP 422, если тело не принято. HTTP 500, если расчёт
    или ставка денег не проходит.
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
    """Откладывает заказ через delay.

    Результат: HTTP 200 и JSON с id и cost_report этого расчёта.
    Побочные эффекты: заказ сохраняется со статусом «Отложен»,
    отчёт дописывается в конец.
    Ошибки: HTTP 404, если заданного id нет. HTTP 422, если тело
    не принято. HTTP 500, если расчёт или ставка не проходит
    и запись не начинается. HTTP 503, если нет соединения с базой.
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
    """Принимает заказ через accept.

    Результат: HTTP 200 и JSON с id и cost_report этого расчёта.
    Побочные эффекты: заказ сохраняется со статусом «В работе»,
    отчёт дописывается в конец.
    Ошибки: HTTP 404, если заданного id нет. HTTP 422, если тело
    не принято. HTTP 500, если расчёт или ставка не проходит
    и запись не начинается. HTTP 503, если нет соединения с базой.
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
    """Меняет статус заказа через change_status.

    Результат: HTTP 200 без тела.
    Побочные эффекты: меняется только статус. Отчёт не пишется.
    Ошибки: HTTP 404, если заказа нет. HTTP 422, если тело
    не принято. HTTP 503, если нет соединения с базой.
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
    """Возвращает заказ рабочего места через take.

    Результат: HTTP 200 и JSON заказа без отчётов.
    Ошибки: HTTP 404, если заказа нет. HTTP 422, если id пути
    не целое. HTTP 503, если нет соединения с базой.
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
    """Удаляет заказ рабочего места через delete.

    Результат: HTTP 200 без тела.
    Побочные эффекты: заказ, расчёт и отчёты удаляются.
    Ошибки: HTTP 404, если заказа нет. HTTP 422, если id пути
    не целое. HTTP 503, если нет соединения с базой.
    """
    _call(lambda: service.delete(id))
    return Response(status_code=200)
