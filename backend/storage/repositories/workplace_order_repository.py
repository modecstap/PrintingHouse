from collections.abc import Callable
from typing import TypeVar

from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import InterfaceError, OperationalError
from sqlalchemy.orm import Session

from backend.core.order import Order
from backend.core.order_repository import (
    OrderId,
    OrderNotFound,
    OrderStoreUnavailable,
    StoreOperation,
    WorkplaceOrderRepository,
)
from backend.core.reports import CostReport
from backend.storage.repositories.workplace_order_mapping import (
    insert_order,
    read_order,
    read_reference,
    read_reports,
    update_order,
    write_reference,
    write_report,
)
from backend.storage.tables.workplace_order import CostReportRow, WorkplaceOrderRow

_T = TypeVar("_T")


class SqlWorkplaceOrderRepository(WorkplaceOrderRepository):
    def __init__(self, engine: Engine) -> None:
        """Remembers the Engine.

        :param engine:
        """
        self._engine = engine

    def save(self, order: Order) -> OrderId:
        """Saves the order's calculation data, comment, and status.

        :param order:

        :raises OrderNotFound: if the given id has no row.
        :raises OrderStoreUnavailable: if there is no connection.

        :return: the id of the saved order. When the id is empty,
        the database assigns it, and it is known only from the return.
        When the id already exists, that same id is returned.
        """
        return self._call(
            "save",
            order.id,
            lambda session: self._save(session, order),
        )

    def take(self, order_id: OrderId) -> Order:
        """Returns the whole order with this id, without the CostReport list.

        :param order_id:

        :raises OrderNotFound: if there is no row.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the order with calculation data, comment, status,
        and the insertion date.
        """
        return self._call(
            "take",
            order_id,
            lambda session: self._take(session, order_id),
        )

    def attach(self, report: CostReport, order_id: OrderId) -> None:
        """Appends one report to the end of the order's report list.

        :param report:
        :param order_id:

        :raises OrderNotFound: if the order does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        self._call(
            "attach",
            order_id,
            lambda session: self._attach(session, report, order_id),
        )

    def reports(self, order_id: OrderId) -> list[CostReport]:
        """Returns the order's attached reports.

        :param order_id:

        :raises OrderNotFound: if the order does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: an empty list if attach has not happened yet.
        Otherwise the reports are in the order of successful attach calls,
        from the earliest.
        """
        return self._call(
            "reports",
            order_id,
            lambda session: self._reports(session, order_id),
        )

    def take_all(self) -> list[Order]:
        """Returns every order row, without CostReport.

        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: each row once, by descending id. No rows: an empty list.
        """
        return self._call(
            "take_all",
            None,
            lambda session: self._take_all(session),
        )

    def delete(self, order_id: OrderId) -> None:
        """Deletes this order.

        :param order_id:

        :raises OrderNotFound: if the order does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        self._call(
            "delete",
            order_id,
            lambda session: self._delete(session, order_id),
        )

    def save_with_report(
        self, order: Order, report: CostReport
    ) -> OrderId:
        """Saves the order and appends the report in one transaction.

        :param order:
        :param report:

        :raises OrderNotFound: if the given id has no row. The text is built by save.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the id of the saved order. An empty id is assigned by the database.
        An existing id is returned unchanged.
        """
        return self._call(
            "save_with_report",
            order.id,
            lambda session: self._save_with_report(
                session, order, report
            ),
        )

    def reference(self) -> Order | None:
        """Returns the reference if the row exists.

        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: an order with id None and no creation_date. No row: None.
        """
        return self._call(
            "reference",
            None,
            lambda session: read_reference(session),
        )

    def set_reference(self, order: Order) -> None:
        """Replaces the single reference record.

        :param order:

        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
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
