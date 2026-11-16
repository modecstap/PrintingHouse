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

        :param cutters: the cutters.
        :param cutter_factory: the cutter factory.
        """
        self._cutters = cutters
        self._cutter_factory = cutter_factory

    def cutters(self) -> tuple[Cutter, ...]:
        """Returns every stored cutter.

        :return: the tuple[Cutter, ...] result.
        """
        return self._cutters.take_all()

    def cutter(self, cutter_id: CutterID) -> Cutter:
        """Returns one cutter.

        :param cutter_id: id of the cutter.

        :raises KeyError: if there is no cutter.

        :return: the Cutter result.
        """
        return self._cutters.take(cutter_id)

    def save_cutter(self, cutter: Cutter) -> None:
        """Stores a new cutter under its id.

        :param cutter: the cutter.
        """
        self._cutters.save(cutter)

    def create_cutter(self, name: str, max_stack: int) -> CutterID:
        """Inserts a new cutter; the store assigns the id.

        :param name: the name.
        :param max_stack: the max stack.

        :return: the CutterID result.
        """
        cutter = self._cutter_factory.create(name, max_stack)
        self._cutters.save(cutter)
        return cutter.id

    def replace_cutter(self, cutter: Cutter) -> None:
        """Overwrites non-id fields of an existing cutter.

        :param cutter:

        :raises KeyError: if there is no cutter with this id.
        """
        self._cutters.replace(cutter)

    def delete_cutter(self, cutter_id: CutterID) -> None:
        """Removes a cutter.

        :param cutter_id:

        :raises KeyError: if there is no cutter.
        """
        self._cutters.delete(cutter_id)
