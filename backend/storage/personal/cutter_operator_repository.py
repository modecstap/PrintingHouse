"""SQL implementation of ``CutterOperatorRepository``."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.new_core.personal.cutter_operator import CutterOperator, CutterOperatorID
from backend.new_core.personal.cutter_operator_repository import CutterOperatorIdOccupied
from backend.new_core.values.money import Money
from backend.storage.personal.tables import CutterOperatorRow


class SqlCutterOperatorRepository:
    """Loads and stores cutter operators in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, operator_id: CutterOperatorID) -> CutterOperator:
        """Returns the cutter operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: the operator row.
        """
        row = self._session.get(CutterOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        return CutterOperator(
            id=operator_id,
            salary_by_operation=Money(row.salary_by_operation),
        )

    def take_all(self) -> tuple[CutterOperator, ...]:
        """Returns every stored cutter operator.

        :return: operators in ascending id order.
        """
        stmt = select(CutterOperatorRow).order_by(CutterOperatorRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            CutterOperator(
                id=CutterOperatorID(row.id),
                salary_by_operation=Money(row.salary_by_operation),
            )
            for row in rows
        )

    def save(self, operator: CutterOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises CutterOperatorIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        try:
            self._session.add(
                CutterOperatorRow(
                    id=operator.id.value,
                    salary_by_operation=operator.salary_by_operation.amount,
                ),
            )
            self._session.flush()
        except IntegrityError as exc:
            raise CutterOperatorIdOccupied("save", operator.id) from exc

    def delete(self, operator_id: CutterOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: nothing.
        """
        row = self._session.get(CutterOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        self._session.delete(row)
