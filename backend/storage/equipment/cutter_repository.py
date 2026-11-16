"""SQL implementation of ``CutterRepository``."""

from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.new_core.equipment.cutter import Cutter, CutterID
from backend.new_core.equipment.cutter_repository import CutterIdOccupied
from backend.storage.equipment.tables import CutterRow


__all__ = ["SqlCutterRepository"]

class SqlCutterRepository:
    """Loads and stores cutters in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        """Initializes this instance.

        :param session: database session.
        """
        self._session = session

    def take(self, cutter_id: CutterID) -> Cutter:
        """Returns the cutter with this id.

        :param cutter_id: id of the cutter.

        :raises KeyError: if there is no cutter.

        :return: the Cutter result.
        """
        row = self._session.get(CutterRow, cutter_id.value)
        if row is None:
            raise KeyError(cutter_id)
        return Cutter(id=cutter_id, name=row.name, max_stack=row.max_stack)

    def take_all(self) -> tuple[Cutter, ...]:
        """Returns every stored cutter.

        :return: the tuple[Cutter, ...] result.
        """
        stmt = select(CutterRow).order_by(CutterRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            Cutter(id=CutterID(row.id), name=row.name, max_stack=row.max_stack)
            for row in rows
        )

    def generate_id(self) -> CutterID:
        """Returns the next cutter id from the store sequence.

        :return: the CutterID result.
        """
        value = self._session.execute(
            text("SELECT nextval('cutter_id_seq')"),
        ).scalar_one()
        return CutterID(int(value))

    def save(self, cutter: Cutter) -> None:
        """Stores the cutter under its id.

        :param cutter:

        :raises CutterIdOccupied: if that id is already stored.
        """
        try:
            self._session.add(
                CutterRow(
                    id=cutter.id.value,
                    name=cutter.name,
                    max_stack=cutter.max_stack,
                ),
            )
            self._session.flush()
        except IntegrityError as exc:
            raise CutterIdOccupied("save", cutter.id) from exc

    def replace(self, cutter: Cutter) -> None:
        """Overwrites non-id fields of an existing cutter.

        :param cutter:

        :raises KeyError: if there is no cutter with this id.
        """
        row = self._session.get(CutterRow, cutter.id.value)
        if row is None:
            raise KeyError(cutter.id)
        row.name = cutter.name
        row.max_stack = cutter.max_stack
        self._session.flush()

    def delete(self, cutter_id: CutterID) -> None:
        """Removes the cutter with this id.

        :param cutter_id:

        :raises KeyError: if there is no cutter.
        """
        row = self._session.get(CutterRow, cutter_id.value)
        if row is None:
            raise KeyError(cutter_id)
        self._session.delete(row)
