"""Laminator catalog use cases."""

from __future__ import annotations

from backend.new_core.equipment.factory import LaminatorFactory
from backend.new_core.equipment.laminator import Laminator, LaminatorID
from backend.new_core.equipment.laminator_repository import LaminatorRepository
from backend.new_core.values.money import Money


__all__ = ["LaminatorCatalog"]

class LaminatorCatalog:
    """Loads and edits laminators."""

    def __init__(
        self,
        laminators: LaminatorRepository,
        laminator_factory: LaminatorFactory,
    ) -> None:
        """Remembers the laminator store.

        :param laminators:
        :param laminator_factory:
        """
        self._laminators = laminators
        self._laminator_factory = laminator_factory

    def laminators(self) -> tuple[Laminator, ...]:
        """Returns every stored laminator.

        :return: laminators in ascending id order.
        """
        return self._laminators.take_all()

    def laminator(self, laminator_id: LaminatorID) -> Laminator:
        """Returns one laminator.

        :param laminator_id:

        :raises KeyError: if there is no laminator.

        :return: the laminator row.
        """
        return self._laminators.take(laminator_id)

    def save_laminator(self, laminator: Laminator) -> None:
        """Stores a new laminator under its id.

        :param laminator:

        :return: nothing. Existing rows are not overwritten.
        """
        self._laminators.save(laminator)

    def create_laminator(self, name: str, startup: Money) -> LaminatorID:
        """Inserts a new laminator; the store assigns the id.

        :param name:
        :param startup:

        :return: the assigned laminator id.
        """
        laminator = self._laminator_factory.create(name, startup)
        self._laminators.save(laminator)
        return laminator.id

    def replace_laminator(self, laminator: Laminator) -> None:
        """Overwrites non-id fields of an existing laminator.

        :param laminator:

        :raises KeyError: if there is no laminator with this id.

        :return: nothing.
        """
        self._laminators.replace(laminator)

    def delete_laminator(self, laminator_id: LaminatorID) -> None:
        """Removes a laminator.

        :param laminator_id:

        :raises KeyError: if there is no laminator.

        :return: nothing.
        """
        self._laminators.delete(laminator_id)
