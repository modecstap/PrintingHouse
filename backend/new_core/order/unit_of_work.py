"""Atomic persistence of orders and print runs."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, TypeVar

from backend.new_core.order.repository import OrderRepository
from backend.new_core.print_run.repository import PrintRunRepository

T = TypeVar("T")


class OrderUnitOfWork(Protocol):
    """Orders and print runs written in one transaction."""

    orders: OrderRepository
    print_runs: PrintRunRepository

    def transaction(self, work: Callable[[], T]) -> T:
        """Runs work and rolls back stored rows on any exception.

        :param work:

        :return: the value from work.

        :raises Exception: re-raises whatever work raised after rollback.
        """
        ...
