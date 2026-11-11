"""SQL implementation of ``OrderRepository``."""

from __future__ import annotations

from sqlalchemy import delete, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.new_core.order.additional_work import AdditionalWork
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.product import Product
from backend.new_core.order.repository import OrderIdOccupied, OrderNotFound
from backend.new_core.values.money import Money
from backend.new_core.values.percent import Percent
from backend.storage.order.tables import (
    OrderAdditionalWorkRow,
    OrderBlockRow,
    OrderRow,
)
from backend.storage.part.mapping import part_row_to_part, persist_part
from backend.storage.part.tables import PartRow


class SqlOrderRepository:
    """Persists customer orders in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, order_id: OrderID) -> Order:
        """Returns the order with this id.

        :param order_id:

        :raises OrderNotFound: if there is no order.

        :return: the order row.
        """
        row = self._session.get(OrderRow, order_id.value)
        if row is None:
            raise OrderNotFound("take", order_id)
        return self._order_from_rows(order_id, row)

    def generate_id(self) -> OrderID:
        """Returns the next order id from the store sequence.

        :return: a new order id. It may already be occupied.
        """
        value = self._session.execute(
            text("SELECT nextval('order_id_seq')"),
        ).scalar_one()
        return OrderID(int(value))

    def save(self, order: Order) -> None:
        """Stores the order under its id.

        :param order:

        :raises OrderIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        try:
            self._session.add(
                OrderRow(
                    id=order.id.value,
                    count=order.count,
                    description=order.description,
                    created_at=order.created_at,
                ),
            )
            self._session.flush()
        except IntegrityError as exc:
            raise OrderIdOccupied("save", order.id) from exc

        for position, work in enumerate(order.product.operations):
            self._session.add(
                OrderAdditionalWorkRow(
                    order_id=order.id.value,
                    position=position,
                    name=work.name,
                    price=work.price.amount,
                    description=work.description,
                    markup=work.markup.value,
                ),
            )

        for position, block in enumerate(order.product.blocks):
            part_id = persist_part(self._session, block)
            self._session.add(
                OrderBlockRow(
                    order_id=order.id.value,
                    position=position,
                    part_id=part_id,
                ),
            )

    def replace(self, order: Order) -> None:
        """Overwrites an existing order and its product graph.

        :param order:

        :raises OrderNotFound: if there is no order with this id.

        :return: nothing.
        """
        row = self._session.get(OrderRow, order.id.value)
        if row is None:
            raise OrderNotFound("replace", order.id)

        row.count = order.count
        row.description = order.description

        self._session.execute(
            delete(OrderAdditionalWorkRow).where(
                OrderAdditionalWorkRow.order_id == order.id.value,
            ),
        )

        part_ids = self._session.execute(
            select(OrderBlockRow.part_id).where(
                OrderBlockRow.order_id == order.id.value,
            ),
        ).scalars().all()

        self._session.execute(
            delete(OrderBlockRow).where(
                OrderBlockRow.order_id == order.id.value,
            ),
        )
        for part_id in part_ids:
            self._session.execute(delete(PartRow).where(PartRow.id == part_id))

        for position, work in enumerate(order.product.operations):
            self._session.add(
                OrderAdditionalWorkRow(
                    order_id=order.id.value,
                    position=position,
                    name=work.name,
                    price=work.price.amount,
                    description=work.description,
                    markup=work.markup.value,
                ),
            )

        for position, block in enumerate(order.product.blocks):
            part_id = persist_part(self._session, block)
            self._session.add(
                OrderBlockRow(
                    order_id=order.id.value,
                    position=position,
                    part_id=part_id,
                ),
            )

    def take_latest(self, limit: int) -> tuple[Order, ...]:
        """Returns stored orders with the largest ids first.

        :param limit: maximum row count. Zero: an empty tuple.

        :return: at most ``limit`` orders, by descending id.
        No rows: an empty tuple.
        """
        if limit <= 0:
            return ()
        stmt = (
            select(OrderRow)
            .order_by(OrderRow.id.desc())
            .limit(limit)
        )
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            self._order_from_rows(OrderID(row.id), row) for row in rows
        )

    def _order_from_rows(self, order_id: OrderID, row: OrderRow) -> Order:
        blocks_stmt = (
            select(OrderBlockRow)
            .where(OrderBlockRow.order_id == order_id.value)
            .order_by(OrderBlockRow.position)
        )
        block_rows = self._session.execute(blocks_stmt).scalars().all()
        blocks = tuple(
            part_row_to_part(self._session, block_row.part_id)
            for block_row in block_rows
        )

        works_stmt = (
            select(OrderAdditionalWorkRow)
            .where(OrderAdditionalWorkRow.order_id == order_id.value)
            .order_by(OrderAdditionalWorkRow.position)
        )
        work_rows = self._session.execute(works_stmt).scalars().all()
        operations = tuple(
            AdditionalWork(
                name=work_row.name,
                price=Money(work_row.price),
                description=work_row.description,
                markup=Percent(work_row.markup),
            )
            for work_row in work_rows
        )

        return Order(
            id=order_id,
            product=Product(blocks=blocks, operations=operations),
            count=row.count,
            description=row.description,
            created_at=row.created_at,
        )
