"""SQL implementation of ``LaminatorOperatorRepository``."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)
from backend.new_core.values.money import Money
from backend.storage.personal.tables import LaminatorOperatorRow


class SqlLaminatorOperatorRepository:
    """Loads laminator operators from PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, operator_id: LaminatorOperatorID) -> LaminatorOperator:
        """Returns the laminator operator with this id.

        :param operator_id:

        :return: the operator row.
        """
        row = self._session.get(LaminatorOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        return LaminatorOperator(
            id=operator_id,
            salary_by_operation=Money(row.salary_by_operation),
        )
