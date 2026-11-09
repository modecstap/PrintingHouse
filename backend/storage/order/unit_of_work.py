"""SQL implementation of ``OrderUnitOfWork``."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from sqlalchemy.orm import Session

from backend.storage.order.repository import SqlOrderRepository
from backend.storage.print_run.repository import SqlPrintRunRepository

T = TypeVar("T")


class SqlOrderUnitOfWork:
    """Orders and print runs written in one database transaction."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self.orders = SqlOrderRepository(session)
        self.print_runs = SqlPrintRunRepository(session)

    def transaction(self, work: Callable[[], T]) -> T:
        """Runs work and rolls back stored rows on any exception.

        :param work:

        :return: the value from work.

        :raises Exception: re-raises whatever work raised after rollback.
        """
        with self._session.begin():
            return work()
