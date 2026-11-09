"""SQL implementation of ``LaminatorOperatorRepository``."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)
from backend.new_core.personal.laminator_operator_repository import (
    LaminatorOperatorIdOccupied,
)
from backend.new_core.values.money import Money
from backend.storage.personal.tables import LaminatorOperatorRow


class SqlLaminatorOperatorRepository:
    """Loads and stores laminator operators in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, operator_id: LaminatorOperatorID) -> LaminatorOperator:
        """Returns the laminator operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: the operator row.
        """
        row = self._session.get(LaminatorOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        return LaminatorOperator(
            id=operator_id,
            salary_by_operation=Money(row.salary_by_operation),
        )

    def take_all(self) -> tuple[LaminatorOperator, ...]:
        """Returns every stored laminator operator.

        :return: operators in ascending id order.
        """
        stmt = select(LaminatorOperatorRow).order_by(LaminatorOperatorRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            LaminatorOperator(
                id=LaminatorOperatorID(row.id),
                salary_by_operation=Money(row.salary_by_operation),
            )
            for row in rows
        )

    def save(self, operator: LaminatorOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises LaminatorOperatorIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        try:
            self._session.add(
                LaminatorOperatorRow(
                    id=operator.id.value,
                    salary_by_operation=operator.salary_by_operation.amount,
                ),
            )
            self._session.flush()
        except IntegrityError as exc:
            raise LaminatorOperatorIdOccupied("save", operator.id) from exc

    def delete(self, operator_id: LaminatorOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: nothing.
        """
        row = self._session.get(LaminatorOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        self._session.delete(row)
