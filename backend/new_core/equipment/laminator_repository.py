"""Laminator catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.equipment.laminator import Laminator, LaminatorID


class LaminatorRepository(Protocol):
    """Loads laminators by id."""

    def take(self, laminator_id: LaminatorID) -> Laminator:
        """Returns the laminator with this id.

        :param laminator_id:

        :return: the laminator row.
        """
        ...
