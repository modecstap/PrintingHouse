"""SQL implementation of ``DieCutterOperatorRepository``."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.new_core.personal.die_cutter_operator_repository import (
    DieCutterOperatorIdOccupied,
)
from backend.new_core.values.money import Money
from backend.storage.personal.tables import DieCutterOperatorRow


class SqlDieCutterOperatorRepository:
    """Loads and stores die cutter operators in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, operator_id: DieCutterOperatorID) -> DieCutterOperator:
        """Returns the die cutter operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: the operator row.
        """
        row = self._session.get(DieCutterOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        return DieCutterOperator(
            id=operator_id,
            salary_by_operation=Money(row.salary_by_operation),
        )

    def take_all(self) -> tuple[DieCutterOperator, ...]:
        """Returns every stored die-cut operator.

        :return: operators in ascending id order.
        """
        stmt = select(DieCutterOperatorRow).order_by(DieCutterOperatorRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            DieCutterOperator(
                id=DieCutterOperatorID(row.id),
                salary_by_operation=Money(row.salary_by_operation),
            )
            for row in rows
        )

    def save(self, operator: DieCutterOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises DieCutterOperatorIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        try:
            self._session.add(
                DieCutterOperatorRow(
                    id=operator.id.value,
                    salary_by_operation=operator.salary_by_operation.amount,
                ),
            )
            self._session.flush()
        except IntegrityError as exc:
            raise DieCutterOperatorIdOccupied("save", operator.id) from exc

    def delete(self, operator_id: DieCutterOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: nothing.
        """
        row = self._session.get(DieCutterOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        self._session.delete(row)
