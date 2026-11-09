"""SQL implementation of ``CutterOperatorRepository``."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.new_core.personal.cutter_operator import CutterOperator, CutterOperatorID
from backend.new_core.values.money import Money
from backend.storage.personal.tables import CutterOperatorRow


class SqlCutterOperatorRepository:
    """Loads cutter operators from PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, operator_id: CutterOperatorID) -> CutterOperator:
        """Returns the cutter operator with this id.

        :param operator_id:

        :return: the operator row.
        """
        row = self._session.get(CutterOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        return CutterOperator(
            id=operator_id,
            salary_by_operation=Money(row.salary_by_operation),
        )
