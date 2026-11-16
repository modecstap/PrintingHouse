"""SQL implementation of ``PressOperatorRepository``."""

from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.new_core.personal.press_operator import (
    PressOperator,
    PressOperatorID,
)
from backend.new_core.personal.press_operator_repository import (
    PressOperatorIdOccupied,
)
from backend.new_core.values.money import Money
from backend.storage.personal.operator_row import (
    replace_operator_row,
    save_operator_row,
)
from backend.storage.personal.tables import PressOperatorRow


class SqlPressOperatorRepository:
    """Loads and stores press operators in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, operator_id: PressOperatorID) -> PressOperator:
        """Returns the press operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: the operator row.
        """
        row = self._session.get(PressOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        return PressOperator(
            id=operator_id,
            name=row.name,
            salary_by_operation=Money(row.salary_by_operation),
        )

    def take_all(self) -> tuple[PressOperator, ...]:
        """Returns every stored press operator.

        :return: operators in ascending id order.
        """
        stmt = select(PressOperatorRow).order_by(PressOperatorRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            PressOperator(
                id=PressOperatorID(row.id),
                name=row.name,
                salary_by_operation=Money(row.salary_by_operation),
            )
            for row in rows
        )

    def generate_id(self) -> PressOperatorID:
        """Returns the next press operator id from the store sequence.

        :return: a new operator id. It may already be occupied.
        """
        value = self._session.execute(
            text("SELECT nextval('press_operator_id_seq')"),
        ).scalar_one()
        return PressOperatorID(int(value))

    def save(self, operator: PressOperator) -> None:
        """Stores the operator under its id.

        :param operator:

        :raises PressOperatorIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        save_operator_row(
            self._session,
            PressOperatorRow(
                id=operator.id.value,
                name=operator.name,
                salary_by_operation=operator.salary_by_operation.amount,
            ),
            operator.id,
            PressOperatorIdOccupied,
        )

    def replace(self, operator: PressOperator) -> None:
        """Overwrites non-id fields of an existing press operator.

        :param operator:

        :raises KeyError: if there is no operator with this id.

        :return: nothing.
        """
        replace_operator_row(
            self._session,
            self._session.get(PressOperatorRow, operator.id.value),
            operator,
        )

    def delete(self, operator_id: PressOperatorID) -> None:
        """Removes the operator with this id.

        :param operator_id:

        :raises KeyError: if there is no operator.

        :return: nothing.
        """
        row = self._session.get(PressOperatorRow, operator_id.value)
        if row is None:
            raise KeyError(operator_id)
        self._session.delete(row)
