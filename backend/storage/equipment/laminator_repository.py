"""SQL implementation of ``LaminatorRepository``."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.new_core.equipment.laminator import Laminator, LaminatorID
from backend.new_core.equipment.laminator_repository import LaminatorIdOccupied
from backend.new_core.values.money import Money
from backend.storage.equipment.tables import LaminatorRow


class SqlLaminatorRepository:
    """Loads and stores laminators in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, laminator_id: LaminatorID) -> Laminator:
        """Returns the laminator with this id.

        :param laminator_id:

        :raises KeyError: if there is no laminator.

        :return: the laminator row.
        """
        row = self._session.get(LaminatorRow, laminator_id.value)
        if row is None:
            raise KeyError(laminator_id)
        return Laminator(id=laminator_id, startup=Money(row.startup))

    def take_all(self) -> tuple[Laminator, ...]:
        """Returns every stored laminator.

        :return: laminators in ascending id order.
        """
        stmt = select(LaminatorRow).order_by(LaminatorRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            Laminator(id=LaminatorID(row.id), startup=Money(row.startup))
            for row in rows
        )

    def save(self, laminator: Laminator) -> None:
        """Stores the laminator under its id.

        :param laminator:

        :raises LaminatorIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        try:
            self._session.add(
                LaminatorRow(
                    id=laminator.id.value,
                    startup=laminator.startup.amount,
                ),
            )
            self._session.flush()
        except IntegrityError as exc:
            raise LaminatorIdOccupied("save", laminator.id) from exc

    def delete(self, laminator_id: LaminatorID) -> None:
        """Removes the laminator with this id.

        :param laminator_id:

        :raises KeyError: if there is no laminator.

        :return: nothing.
        """
        row = self._session.get(LaminatorRow, laminator_id.value)
        if row is None:
            raise KeyError(laminator_id)
        self._session.delete(row)
