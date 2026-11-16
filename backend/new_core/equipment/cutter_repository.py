"""Cutter catalog contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.equipment.cutter import Cutter, CutterID

__all__ = [
    "CutterIdOccupied",
    "CutterRepository",
]

CutterStoreOperation = Literal["save"]


class CutterIdOccupied(CatalogIdOccupied):
    """Reports that a cutter id is already stored."""

    def __init__(
        self,
        operation: CutterStoreOperation,
        cutter_id: CutterID,
    ) -> None:
        """Builds the repository error text.

        :param operation: the operation.
        :param cutter_id: id of the cutter.
        """
        super().__init__(
            f"{operation}: резак уже есть, id={cutter_id.value}",
        )


class CutterRepository(Protocol):
    """Loads and stores cutters by id."""

    def take(self, cutter_id: CutterID) -> Cutter:
        """Returns the cutter with this id.

        :param cutter_id: id of the cutter.

        :raises KeyError: if there is no cutter.
"""
        ...

    def take_all(self) -> tuple[Cutter, ...]:
        """Returns every stored cutter.
"""
        ...

    def generate_id(self) -> CutterID:
        """Returns the next cutter id from the store sequence.
"""
        ...

    def save(self, cutter: Cutter) -> None:
        """Stores the cutter under its id.

        :param cutter:

        :raises CutterIdOccupied: if that id is already stored.
        """
        ...

    def replace(self, cutter: Cutter) -> None:
        """Overwrites non-id fields of an existing cutter.

        :param cutter:

        :raises KeyError: if there is no cutter with this id.
        """
        ...

    def delete(self, cutter_id: CutterID) -> None:
        """Removes the cutter with this id.

        :param cutter_id:

        :raises KeyError: if there is no cutter.
        """
        ...
