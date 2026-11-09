"""Cutter catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.equipment.cutter import Cutter, CutterID


class CutterRepository(Protocol):
    """Loads cutters by id."""

    def take(self, cutter_id: CutterID) -> Cutter:
        """Returns the cutter with this id.

        :param cutter_id:

        :return: the cutter row.
        """
        ...
