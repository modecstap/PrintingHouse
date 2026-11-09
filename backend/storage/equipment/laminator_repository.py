"""SQL implementation of ``LaminatorRepository``."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.new_core.equipment.laminator import Laminator, LaminatorID
from backend.new_core.values.money import Money
from backend.storage.equipment.tables import LaminatorRow


class SqlLaminatorRepository:
    """Loads laminators from PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, laminator_id: LaminatorID) -> Laminator:
        """Returns the laminator with this id.

        :param laminator_id:

        :return: the laminator row.
        """
        row = self._session.get(LaminatorRow, laminator_id.value)
        if row is None:
            raise KeyError(laminator_id)
        return Laminator(
            id=laminator_id,
            startup=Money(row.startup),
        )
