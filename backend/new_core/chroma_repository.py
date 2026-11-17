"""Chroma catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.chroma import Chroma, ChromaID


__all__ = ["ChromaRepository"]


class ChromaRepository(Protocol):
    """Loads and stores chroma rows by id."""

    def take(self, chroma_id: ChromaID) -> Chroma:
        """Returns the chroma row with this id.

        :param chroma_id: id of the chroma row.

        :raises KeyError: if there is no row.
        """
        ...

    def take_all(self) -> tuple[Chroma, ...]:
        """Returns every stored chroma row."""
        ...

    def add(
        self,
        name: str,
        cyan: int,
        magenta: int,
        yellow: int,
        black: int,
    ) -> ChromaID:
        """Inserts a new row; the store assigns the id.

        :param name: the name.
        :param cyan: cyan fill percent.
        :param magenta: magenta fill percent.
        :param yellow: yellow fill percent.
        :param black: black fill percent.
        """
        ...

    def replace(self, chroma: Chroma) -> None:
        """Overwrites non-id fields of an existing row.

        :param chroma:

        :raises KeyError: if there is no row with this id.
        """
        ...

    def delete(self, chroma_id: ChromaID) -> None:
        """Removes the row with this id.

        :param chroma_id:

        :raises KeyError: if there is no row.
        """
        ...

    def find_or_add(
        self,
        name: str,
        cyan: int,
        magenta: int,
        yellow: int,
        black: int,
    ) -> ChromaID:
        """Returns an existing row matching name and fills or inserts one."""
        ...