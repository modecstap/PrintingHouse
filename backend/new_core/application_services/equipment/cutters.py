"""Cutter catalog use cases."""

from __future__ import annotations

from backend.new_core.equipment.cutter import Cutter, CutterID
from backend.new_core.equipment.cutter_repository import CutterRepository
from backend.new_core.equipment.factory import CutterFactory


__all__ = ["CutterCatalog"]

class CutterCatalog:
    """Loads and edits cutters."""

    def __init__(
        self,
        cutters: CutterRepository,
        cutter_factory: CutterFactory,
    ) -> None:
        """Remembers the cutter store.

        :param cutters:
        :param cutter_factory:
        """
        self._cutters = cutters
        self._cutter_factory = cutter_factory

    def cutters(self) -> tuple[Cutter, ...]:
        """Returns every stored cutter.

        :return: cutters in ascending id order.
        """
        return self._cutters.take_all()

    def cutter(self, cutter_id: CutterID) -> Cutter:
        """Returns one cutter.

        :param cutter_id:

        :raises KeyError: if there is no cutter.

        :return: the cutter row.
        """
        return self._cutters.take(cutter_id)

    def save_cutter(self, cutter: Cutter) -> None:
        """Stores a new cutter under its id.

        :param cutter:

        :return: nothing. Existing rows are not overwritten.
        """
        self._cutters.save(cutter)

    def create_cutter(self, name: str, max_stack: int) -> CutterID:
        """Inserts a new cutter; the store assigns the id.

        :param name:
        :param max_stack:

        :return: the assigned cutter id.
        """
        cutter = self._cutter_factory.create(name, max_stack)
        self._cutters.save(cutter)
        return cutter.id

    def replace_cutter(self, cutter: Cutter) -> None:
        """Overwrites non-id fields of an existing cutter.

        :param cutter:

        :raises KeyError: if there is no cutter with this id.

        :return: nothing.
        """
        self._cutters.replace(cutter)

    def delete_cutter(self, cutter_id: CutterID) -> None:
        """Removes a cutter.

        :param cutter_id:

        :raises KeyError: if there is no cutter.

        :return: nothing.
        """
        self._cutters.delete(cutter_id)
