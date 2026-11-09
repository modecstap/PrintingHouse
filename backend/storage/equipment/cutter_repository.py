"""SQL implementation of ``CutterRepository``."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.new_core.equipment.cutter import Cutter, CutterID
from backend.new_core.equipment.cutter_repository import CutterIdOccupied
from backend.storage.equipment.tables import CutterRow


class SqlCutterRepository:
    """Loads and stores cutters in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, cutter_id: CutterID) -> Cutter:
        """Returns the cutter with this id.

        :param cutter_id:

        :raises KeyError: if there is no cutter.

        :return: the cutter row.
        """
        row = self._session.get(CutterRow, cutter_id.value)
        if row is None:
            raise KeyError(cutter_id)
        return Cutter(id=cutter_id, max_stack=row.max_stack)

    def take_all(self) -> tuple[Cutter, ...]:
        """Returns every stored cutter.

        :return: cutters in ascending id order.
        """
        stmt = select(CutterRow).order_by(CutterRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            Cutter(id=CutterID(row.id), max_stack=row.max_stack) for row in rows
        )

    def save(self, cutter: Cutter) -> None:
        """Stores the cutter under its id.

        :param cutter:

        :raises CutterIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        try:
            self._session.add(
                CutterRow(id=cutter.id.value, max_stack=cutter.max_stack),
            )
            self._session.flush()
        except IntegrityError as exc:
            raise CutterIdOccupied("save", cutter.id) from exc

    def delete(self, cutter_id: CutterID) -> None:
        """Removes the cutter with this id.

        :param cutter_id:

        :raises KeyError: if there is no cutter.

        :return: nothing.
        """
        row = self._session.get(CutterRow, cutter_id.value)
        if row is None:
            raise KeyError(cutter_id)
        self._session.delete(row)
