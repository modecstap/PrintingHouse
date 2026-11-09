"""SQL implementation of ``CutterRepository``."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.new_core.equipment.cutter import Cutter, CutterID
from backend.storage.equipment.tables import CutterRow


class SqlCutterRepository:
    """Loads cutters from PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, cutter_id: CutterID) -> Cutter:
        """Returns the cutter with this id.

        :param cutter_id:

        :return: the cutter row.
        """
        row = self._session.get(CutterRow, cutter_id.value)
        if row is None:
            raise KeyError(cutter_id)
        return Cutter(id=cutter_id, max_stack=row.max_stack)
