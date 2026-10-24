from collections.abc import Callable
from typing import Literal, TypeVar

from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import InterfaceError, OperationalError
from sqlalchemy.orm import Session

from backend.workplace.cost_order import Order
from backend.workplace.order_repository import (
    OrderId,
    OrderNotFound,
    OrderStoreUnavailable,
    WorkplaceOrderRepository,
)
from backend.workplace.reports import CostReport
from backend.workplace_order_db.mapping import (
    insert_order,
    read_order,
    read_reports,
    update_order,
    write_report,
)
from backend.workplace_order_db.tables import CostReportRow, WorkplaceOrderRow

_T = TypeVar("_T")


class SqlWorkplaceOrderRepository(WorkplaceOrderRepository):
    def __init__(self, engine: Engine) -> None:
        """Запоминает Engine. Переменные окружения не читает."""
        self._engine = engine

    def save(self, order: Order) -> OrderId:
        """Сохраняет данные расчёта, comment и status заказа.

        Результат: id сохранённого заказа. Пустой id назначает база,
        и он известен только из возврата. Существующий id возвращается
        тем же.
        Побочные эффекты: пустой id вставляет строку и не пишет
        CostReport. Существующий id заменяет данные расчёта, comment
        и status. Уже прикреплённые отчёты не удаляются и не меняют
        порядок. Переданный Order не меняется. Неудачное сохранение
        оставляет уже сохранённые заказы и отчёты как были.
        Ошибки: OrderNotFound, если заданный id без строки, база
        не меняется. OrderStoreUnavailable, если нет соединения.
        """
        return self._call(
            "save",
            order.id,
            lambda session: self._save(session, order),
        )

    def take(self, order_id: OrderId) -> Order:
        """Возвращает весь заказ с этим id, без списка CostReport.

        Результат: заказ с данными расчёта, comment и status.
        Ошибки: OrderNotFound, если строки нет.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        return self._call(
            "take",
            order_id,
            lambda session: self._take(session, order_id),
        )

    def attach(self, report: CostReport, order_id: OrderId) -> None:
        """Дописывает один отчёт в конец списка отчётов заказа.

        Результат: ничего не возвращает.
        Побочные эффекты: число PrintingCost с числом печатей
        не сверяется. Неудачное прикрепление оставляет уже
        сохранённые заказы и отчёты как были.
        Ошибки: OrderNotFound, если заказа нет, отчёт не пишется.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        self._call(
            "attach",
            order_id,
            lambda session: self._attach(session, report, order_id),
        )

    def reports(self, order_id: OrderId) -> list[CostReport]:
        """Возвращает прикреплённые отчёты заказа.

        Результат: пустой список, если attach ещё не было.
        Иначе отчёты в порядке успешных attach, с самого раннего.
        Ошибки: OrderNotFound, если заказа нет.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        return self._call(
            "reports",
            order_id,
            lambda session: self._reports(session, order_id),
        )

    def _call(
        self,
        operation: Literal["save", "take", "attach", "reports"],
        order_id: int | None,
        action: Callable[[Session], _T],
    ) -> _T:
        try:
            with Session(self._engine) as session:
                with session.begin():
                    return action(session)
        except (OperationalError, InterfaceError) as error:
            raise OrderStoreUnavailable(operation, order_id) from error

    def _save(self, session: Session, order: Order) -> OrderId:
        if order.id is None:
            return insert_order(session, order)
        row = session.get(
            WorkplaceOrderRow, order.id, with_for_update=True
        )
        if row is None:
            raise OrderNotFound("save", order.id)
        update_order(session, row, order)
        return order.id

    def _take(self, session: Session, order_id: OrderId) -> Order:
        row = session.get(WorkplaceOrderRow, order_id)
        if row is None:
            raise OrderNotFound("take", order_id)
        return read_order(session, row)

    def _attach(
        self, session: Session, report: CostReport, order_id: OrderId
    ) -> None:
        row = session.get(
            WorkplaceOrderRow, order_id, with_for_update=True
        )
        if row is None:
            raise OrderNotFound("attach", order_id)
        current = session.scalar(
            select(func.max(CostReportRow.position)).where(
                CostReportRow.order_id == order_id
            )
        )
        position = 0 if current is None else current + 1
        write_report(session, report, order_id, position)

    def _reports(
        self, session: Session, order_id: OrderId
    ) -> list[CostReport]:
        row = session.get(WorkplaceOrderRow, order_id)
        if row is None:
            raise OrderNotFound("reports", order_id)
        return read_reports(session, order_id)
