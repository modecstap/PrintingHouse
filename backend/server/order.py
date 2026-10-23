from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import StreamingResponse

from backend.models import Order, OrderCostReport, Status
from backend.server.dependencies import (
    get_current_user_with_full_permission,
    get_current_user_with_read_permission,
)
from backend.server.helpers.order_factory import OrderFactoryService
from backend.server.instruction import get_order_instruction
from backend.server.models.change_payload import ChangePayload
from backend.storage.access_services.accessor_factory import AccessorFactory
from backend.storage.exceptions.not_found_exception import NotFoundException


router = APIRouter(prefix="/api/order", tags=["order"])
_orders = AccessorFactory.get_order_crud_accessor()
_order_factory = OrderFactoryService()


def _divide_edition_count(order: Order) -> None:
    for printing in order.printings:
        printing.edition.count /= order.unit_count


@router.get(
    "/",
    dependencies=[Depends(get_current_user_with_read_permission)],
)
async def list_orders() -> list[Order]:
    """Возвращает заказы. Делит edition.count каждой печати на unit_count заказа.

    Ошибки: HTTP 404 с текстом NotFoundException, если хранилище её бросает.
    """
    try:
        orders = await _orders.get_models()
    except NotFoundException as exception:
        raise HTTPException(404, detail=str(exception))
    for order in orders:
        _divide_edition_count(order)
    return orders


@router.get(
    "/{id}",
    dependencies=[Depends(get_current_user_with_read_permission)],
)
async def get_order(id: int) -> Order:
    """Возвращает заказ по id. Делит edition.count каждой печати на unit_count.

    Ошибки: HTTP 404. Текст: NotFoundException, item with id {id} not found.
    """
    try:
        order = await _orders.get_model_by_id(id)
    except NotFoundException as exception:
        raise HTTPException(404, detail=str(exception))
    _divide_edition_count(order)
    return order


@router.post(
    "/",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
async def create_order(order: Order) -> Order:
    """Сохраняет один заказ без fit_order.

    Результат: заказ, который вернул accessor.
    Побочные эффекты: новая строка заказа.
    """
    return (await _orders.add_models([order]))[0]


@router.post(
    "/bulk",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
async def create_orders(orders: list[Order]) -> list[Order]:
    """Сохраняет список заказов без fit_order.

    Результат: заказы, которые вернул accessor.
    Побочные эффекты: новые строки заказов.
    """
    return await _orders.add_models(orders)


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
async def update_order(id: int, order: Order) -> Order:
    """Пишет id из пути в модель, прогоняет fit_order со статусом заказа и сохраняет.

    Результат: сохранённый заказ.
    Побочные эффекты: обновление строки. edition.count умножается внутри fit_order.
    """
    order.id = id
    fitted = _order_factory.fit_order(order, order.status)
    return (await _orders.update_models([fitted]))[0]


@router.put(
    "/",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
async def update_orders(orders: list[Order]) -> list[Order]:
    """Сохраняет список заказов без fit_order и без подстановки id.

    Результат: заказы, которые вернул accessor.
    Побочные эффекты: обновление строк.
    """
    return await _orders.update_models(orders)


@router.delete(
    "/{id}",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
async def delete_order(id: int) -> dict:
    """Удаляет заказ по id.

    Результат: словарь message и status_code. Поле status_code не задаёт код HTTP.
    Побочные эффекты: удаление строки.
    """
    await _orders.delete_models([id])
    return {"message": "Deleted successfully", "status_code": status.HTTP_200_OK}


@router.post(
    "/cost_report",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def build_order_cost_report(order: Order) -> OrderCostReport:
    """Считает стоимость заказа в памяти. fit_order вызывается со статусом None.

    Результат: cost_report. Заказ не сохраняется.
    """
    fitted = _order_factory.fit_order(order, None)
    return fitted.cost_report


@router.post(
    "/delay",
    dependencies=[Depends(get_current_user_with_full_permission)],
    response_model=None,
)
async def delay_order(order: Order) -> None:
    """Сохраняет заказ со статусом «Отложен» после fit_order.

    Результат: пустое тело.
    Побочные эффекты: новая строка заказа.
    """
    fitted = _order_factory.fit_order(order, Status("Отложен"))
    await _orders.add_models([fitted])
    return None


@router.post(
    "/accept",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
async def accept_order(order: Order) -> StreamingResponse:
    """Сохраняет заказ со статусом «В работе» и возвращает его инструкцию.

    Результат: PDF или ZIP, как GET /api/instruction/{order_id} для сохранённого id.
    Побочные эффекты: новая строка заказа, затем повторная загрузка заказа.
    """
    fitted = _order_factory.fit_order(order, Status("В работе"))
    saved = (await _orders.add_models([fitted]))[0]
    # accept вызывает функцию эндпоинта инструкции: так работает сейчас, новый сервисный слой вне задачи.
    return await get_order_instruction(saved.id)


@router.post(
    "/status",
    dependencies=[Depends(get_current_user_with_full_permission)],
    response_model=None,
)
async def change_order_status(payload: ChangePayload) -> None:
    """Меняет только статус сохранённого заказа. fit_order не вызывается.

    Результат: пустое тело.
    Побочные эффекты: обновление статуса строки.
    Ошибки: NotFoundException, если заказа нет. Здесь она не перехватывается.
    """
    order = await _orders.get_model_by_id(payload.order_id)
    order.status = payload.new_status
    await _orders.update_models([order])
    return None
