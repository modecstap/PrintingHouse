"""Protected order HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from backend.new_core.application_services.order import OrderService
from backend.new_core.order.order import OrderContent, OrderID
from backend.server.dependencies import get_order_service, require_user
from backend.server.mapping import order_to_dto, product_from_dto, report_to_dto
from backend.server.schemas import (
    OrderDto,
    OrderReportDto,
    OrderWriteDto,
    SaveOrderResponseDto,
)

__all__ = [
    "list_orders",
    "get_order",
    "get_order_report",
    "quote_order",
    "save_order",
    "replace_order",
]

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=list[OrderDto])
def list_orders(
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[OrderService, Depends(get_order_service)],
    limit: int = 50,
) -> list[OrderDto]:
    """Returns the newest orders up to ``limit``.

    :param service: the service.
    :param limit: the limit.

    :return: the list[OrderDto] result.
    """
    return [order_to_dto(order) for order in service.get_orders(limit)]


@router.get("/{order_id}", response_model=OrderDto)
def get_order(
    order_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderDto:
    """Returns one order by id.

    :param order_id: id of the order.
    :param service: the service.

    :return: the OrderDto result.
    """
    return order_to_dto(service.get_order(OrderID(order_id)))


@router.get("/{order_id}/report", response_model=OrderReportDto)
def get_order_report(
    order_id: int,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderReportDto:
    """Returns the price report for an order.

    :param order_id: id of the order.
    :param service: the service.

    :return: the OrderReportDto result.
    """
    return report_to_dto(service.order_report(OrderID(order_id)))


@router.post("/quote", response_model=OrderReportDto)
def quote_order(
    body: OrderWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderReportDto:
    """Prices a product without persisting.

    :param body: request body payload.
    :param service: the service.

    :return: the OrderReportDto result.
    """
    product = product_from_dto(body.product)
    return report_to_dto(service.quote(product, body.count))


@router.post("", response_model=SaveOrderResponseDto)
def save_order(
    body: OrderWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> SaveOrderResponseDto:
    """Persists a new order.

    :param body: request body payload.
    :param service: the service.

    :return: the SaveOrderResponseDto result.
    """
    product = product_from_dto(body.product)
    order_id = service.save(product, body.count, body.description)
    return SaveOrderResponseDto(id=order_id.value)


@router.put("/{order_id}", response_model=SaveOrderResponseDto)
def replace_order(
    order_id: int,
    body: OrderWriteDto,
    _user: Annotated[str, Depends(require_user)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> SaveOrderResponseDto:
    """Replaces an existing order.

    :param order_id: id of the order.
    :param body: request body payload.
    :param service: the service.

    :return: the SaveOrderResponseDto result.
    """
    product = product_from_dto(body.product)
    stored_id = service.replace(
        OrderID(order_id),
        OrderContent(
            product=product,
            count=body.count,
            description=body.description,
        ),
    )
    return SaveOrderResponseDto(id=stored_id.value)
