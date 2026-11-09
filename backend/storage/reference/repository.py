"""SQL implementation of ``ReferenceRepository``."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.new_core.order.order import OrderID
from backend.new_core.reference.reference import Reference
from backend.storage.reference.tables import OrderReferenceRow


class SqlReferenceRepository:
    """Persists named order references in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take_all(self) -> tuple[Reference, ...]:
        """Returns every stored reference.

        :return: references in store order. None: an empty tuple.
        """
        stmt = select(OrderReferenceRow).order_by(OrderReferenceRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            Reference(
                name=row.name,
                description=row.description,
                order_id=OrderID(row.order_id),
            )
            for row in rows
        )

    def save(self, reference: Reference) -> None:
        """Appends a new reference row.

        :param reference:

        :return: nothing. Existing rows are not changed.
        """
        self._session.add(
            OrderReferenceRow(
                name=reference.name,
                description=reference.description,
                order_id=reference.order_id.value,
            ),
        )
