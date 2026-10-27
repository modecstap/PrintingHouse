from collections.abc import Callable
from typing import TypeVar

from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import InterfaceError, OperationalError
from sqlalchemy.orm import Session

from backend.workplace.cost_order import Order
from backend.workplace.order_repository import (
    OrderId,
    OrderNotFound,
    OrderStoreUnavailable,
    StoreOperation,
    WorkplaceOrderRepository,
)
from backend.workplace.reports import CostReport
from backend.workplace_order_db.mapping import (
    insert_order,
    read_order,
    read_reference,
    read_reports,
    update_order,
    write_reference,
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
        Побочные эффекты: пустой id вставляет строку, ставит дату
        процесса и не пишет CostReport. Существующий id заменяет
        данные расчёта, comment и status и дату не меняет. Дата
        аргумента Order не читается. Уже прикреплённые отчёты
        не удаляются и не меняют порядок. Переданный Order не меняется.
        Неудачное сохранение оставляет уже сохранённые заказы и отчёты
        как были.
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

        Результат: заказ с данными расчёта, comment, status и датой
        вставки.
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

    def take_all(self) -> list[Order]:
        """Возвращает все строки workplace_order, без CostReport.

        Результат: каждая строка один раз, по убыванию id.
        Строк нет: пустой список. Заказы таблицы order не читаются.
        Ошибки: OrderStoreUnavailable, если нет соединения с базой.
        OrderNotFound не бросает.
        """
        return self._call(
            "take_all",
            None,
            lambda session: self._take_all(session),
        )

    def delete(self, order_id: OrderId) -> None:
        """Удаляет этот заказ.

        Результат: ничего не возвращает.
        Побочные эффекты: строки расчёта и отчёты уходят каскадом
        базы.
        Ошибки: OrderNotFound, если заказа нет, база не меняется.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        self._call(
            "delete",
            order_id,
            lambda session: self._delete(session, order_id),
        )

    def save_with_report(
        self, order: Order, report: CostReport
    ) -> OrderId:
        """Сохраняет заказ и дописывает отчёт в одной транзакции.

        Результат: id сохранённого заказа. Пустой id вставляет
        заказ, и id назначает база. Существующий id обновляет
        эту строку и возвращается тем же.
        Побочные эффекты: уже прикреплённые отчёты остаются,
        новый становится последним. Переданный Order не меняется.
        Любая ошибка внутри транзакции откатывает и заказ, и отчёт
        этого вызова.
        Ошибки: OrderNotFound, если заданный id без строки:
        новая строка не появляется, отчёт не пишется. Текст
        собирает save. OrderStoreUnavailable, если нет соединения
        с базой.
        """
        return self._call(
            "save_with_report",
            order.id,
            lambda session: self._save_with_report(
                session, order, report
            ),
        )

    def reference(self) -> Order | None:
        """Возвращает справочник, если строка есть.

        Результат: заказ с id None и без creation_date.
        Строки нет: None. OrderNotFound не бросает.
        Ошибки: OrderStoreUnavailable, если нет соединения
        с базой.
        """
        return self._call(
            "reference",
            None,
            lambda session: read_reference(session),
        )

    def set_reference(self, order: Order) -> None:
        """Заменяет единственную запись справочника.

        Результат: ничего не возвращает.
        Побочные эффекты: id аргумента не выбирает запись.
        creation_date в документ не пишется. Строка
        workplace_order не появляется. Два параллельных
        вызова оставляют один целый документ. Переданный
        Order не меняется.
        Ошибки: OrderStoreUnavailable, если нет соединения
        с базой. Чужой id не даёт OrderNotFound.
        """
        self._call(
            "set_reference",
            None,
            lambda session: write_reference(session, order),
        )

    def _call(
        self,
        operation: StoreOperation,
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

    def _take_all(self, session: Session) -> list[Order]:
        rows = session.scalars(
            select(WorkplaceOrderRow).order_by(
                WorkplaceOrderRow.id.desc()
            )
        ).all()
        return [read_order(session, row) for row in rows]

    def _delete(self, session: Session, order_id: OrderId) -> None:
        row = session.get(
            WorkplaceOrderRow, order_id, with_for_update=True
        )
        if row is None:
            raise OrderNotFound("delete", order_id)
        session.delete(row)

    def _save_with_report(
        self, session: Session, order: Order, report: CostReport
    ) -> OrderId:
        order_id = self._save(session, order)
        self._attach(session, report, order_id)
        return order_id
