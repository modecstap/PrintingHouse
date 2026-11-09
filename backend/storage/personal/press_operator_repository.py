"""SQL implementation of ``PressOperatorRepository``."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.new_core.personal.press_operator import PressOperator, PressOperatorID
from backend.new_core.values.money import Money
from backend.storage.personal.tables import PressOperatorRow


class SqlPressOperatorRepository:
    """Loads press operators from PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, operator_id: PressOperatorID) -> PressOperator:
        """Returns the press operator with this id.

        :param operator_id:

        :return: the operator row.
        """
        row = self._session.get(PressOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        return PressOperator(
            id=operator_id,
            salary_by_operation=Money(row.salary_by_operation),
        )
