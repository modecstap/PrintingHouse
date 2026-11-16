"""SQL implementation of ``DieCutterOperatorRepository``."""

from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.new_core.personal.die_cutter_operator_repository import (
    DieCutterOperatorIdOccupied,
)
from backend.new_core.values.money import Money
from backend.storage.personal.operator_row import (
    replace_operator_row,
    save_operator_row,
)
from backend.storage.personal.tables import DieCutterOperatorRow


__all__ = ["SqlDieCutterOperatorRepository"]

class SqlDieCutterOperatorRepository:
    """Loads and stores die cutter operators in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        """Initializes this instance.

        :param session: database session.
        """
        self._session = session

    def take(self, operator_id: DieCutterOperatorID) -> DieCutterOperator:
        """Returns the die cutter operator with this id.

        :param operator_id: id of the operator.

        :raises KeyError: if there is no operator.

        :return: the DieCutterOperator result.
        """
        row = self._session.get(DieCutterOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        return DieCutterOperator(
            id=operator_id,
            name=row.name,
            salary_by_operation=Money(row.salary_by_operation),
        )

    def take_all(self) -> tuple[DieCutterOperator, ...]:
        """Returns every stored die-cut operator.

        :return: the tuple[DieCutterOperator, ...] result.
        """
        stmt = select(DieCutterOperatorRow).order_by(DieCutterOperatorRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            DieCutterOperator(
                id=DieCutterOperatorID(row.id),
                name=row.name,
                salary_by_operation=Money(row.salary_by_operation),
            )
            for row in rows
        )

    def generate_id(self) -> DieCutterOperatorID:
        """Returns the next die cutter operator id from the store sequence.

        :return: the DieCutterOperatorID result.
        """
        value = self._session.execute(
            text("SELECT nextval('die_cutter_operator_id_seq')"),
        ).scalar_one()
        return DieCutterOperatorID(int(value))

    def save(self, operator: DieCutterOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises DieCutterOperatorIdOccupied: if that id is already stored.
        """
        save_operator_row(
            self._session,
            DieCutterOperatorRow(
                id=operator.id.value,
                name=operator.name,
                salary_by_operation=operator.salary_by_operation.amount,
            ),
            operator.id,
            DieCutterOperatorIdOccupied,
        )

    def replace(self, operator: DieCutterOperator) -> None:
        """Overwrites non-id fields of an existing die-cut operator.

        :param operator:

        :raises KeyError: if there is no operator with this id.
        """
        replace_operator_row(
            self._session,
            self._session.get(DieCutterOperatorRow, operator.id.value),
            operator,
        )

    def delete(self, operator_id: DieCutterOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.
        """
        row = self._session.get(DieCutterOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        self._session.delete(row)
