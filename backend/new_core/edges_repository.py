"""Edges catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.edges import Edges, EdgesID


__all__ = ["EdgesRepository"]


class EdgesRepository(Protocol):
    """Loads and stores edges rows by id."""

    def take(self, edges_id: EdgesID) -> Edges:
        """Returns the edges row with this id.

        :param edges_id: id of the edges row.

        :raises KeyError: if there is no row.
        """
        ...

    def take_all(self) -> tuple[Edges, ...]:
        """Returns every stored edges row."""
        ...

    def add(self, name: str, bleeds: int, spacing: int) -> EdgesID:
        """Inserts a new row; the store assigns the id.

        :param name: the name.
        :param bleeds: the bleeds.
        :param spacing: the spacing.
        """
        ...

    def replace(self, edges: Edges) -> None:
        """Overwrites non-id fields of an existing row.

        :param edges:

        :raises KeyError: if there is no row with this id.
        """
        ...

    def delete(self, edges_id: EdgesID) -> None:
        """Removes the row with this id.

        :param edges_id:

        :raises KeyError: if there is no row.
        """
        ...

    def find_or_add(self, name: str, bleeds: int, spacing: int) -> EdgesID:
        """Returns an existing row matching name/bleeds/spacing or inserts one."""
        ...