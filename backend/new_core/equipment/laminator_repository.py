"""Laminator catalog contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.equipment.laminator import Laminator, LaminatorID

LaminatorStoreOperation = Literal["save"]


class LaminatorIdOccupied(CatalogIdOccupied):
    """Reports that a laminator id is already stored."""

    def __init__(
        self,
        operation: LaminatorStoreOperation,
        laminator_id: LaminatorID,
    ) -> None:
        """Builds the repository error text.

        :param operation:
        :param laminator_id:

        :return: sets the message
        ``{operation}: ламинатор уже есть, id={laminator_id.value}``.
        """
        super().__init__(
            f"{operation}: ламинатор уже есть, id={laminator_id.value}",
        )


class LaminatorRepository(Protocol):
    """Loads and stores laminators by id."""

    def take(self, laminator_id: LaminatorID) -> Laminator:
        """Returns the laminator with this id.

        :param laminator_id:

        :raises KeyError: if there is no laminator.

        :return: the laminator row.
        """
        ...

    def take_all(self) -> tuple[Laminator, ...]:
        """Returns every stored laminator.

        :return: laminators in ascending id order.
        """
        ...

    def save(self, laminator: Laminator) -> None:
        """Stores the laminator under its id.

        :param laminator:

        :raises LaminatorIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        ...

    def delete(self, laminator_id: LaminatorID) -> None:
        """Removes the laminator with this id.

        :param laminator_id:

        :raises KeyError: if there is no laminator.

        :return: nothing.
        """
        ...
