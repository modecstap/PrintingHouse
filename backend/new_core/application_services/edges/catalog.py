"""Edges catalog use cases."""

from __future__ import annotations

from backend.new_core.edges import Edges, EdgesID
from backend.new_core.edges_repository import EdgesRepository


__all__ = ["EdgesCatalog"]


class EdgesCatalog:
    """Loads and edits edges catalog rows."""

    def __init__(self, edges: EdgesRepository) -> None:
        """Remembers the edges store.

        :param edges: the edges repository.
        """
        self._edges = edges

    def edges_rows(self) -> tuple[Edges, ...]:
        """Returns every stored edges row.

        :return: the tuple[Edges, ...] result.
        """
        named = (
            edge
            for edge in self._edges.take_all()
            if edge.name != ""
        )
        return named

    def edges_row(self, edges_id: EdgesID) -> Edges:
        """Returns one edges row.

        :param edges_id: id of the edges row.

        :raises KeyError: if there is no row.

        :return: the Edges result.
        """
        return self._edges.take(edges_id)

    def create_edges(
        self,
        name: str,
        bleeds: int,
        spacing: int,
    ) -> EdgesID:
        """Inserts a new row; the store assigns the id.

        :param name: the name.
        :param bleeds: the bleeds.
        :param spacing: the spacing.

        :return: the EdgesID result.
        """
        return self._edges.add(name, bleeds, spacing)

    def replace_edges(self, edges: Edges) -> None:
        """Overwrites non-id fields of an existing row.

        :param edges:

        :raises KeyError: if there is no row with this id.
        """
        self._edges.replace(edges)

    def delete_edges(self, edges_id: EdgesID) -> None:
        """Removes an edges row.

        :param edges_id:

        :raises KeyError: if there is no row.
        """
        self._edges.delete(edges_id)