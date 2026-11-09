"""SQL implementation of ``DieCutterOperatorRepository``."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.new_core.values.money import Money
from backend.storage.personal.tables import DieCutterOperatorRow


class SqlDieCutterOperatorRepository:
    """Loads die cutter operators from PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, operator_id: DieCutterOperatorID) -> DieCutterOperator:
        """Returns the die cutter operator with this id.

        :param operator_id:

        :return: the operator row.
        """
        row = self._session.get(DieCutterOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        return DieCutterOperator(
            id=operator_id,
            salary_by_operation=Money(row.salary_by_operation),
        )
