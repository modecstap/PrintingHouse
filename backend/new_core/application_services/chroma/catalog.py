"""Chroma catalog use cases."""

from __future__ import annotations

from backend.new_core.chroma import Chroma, ChromaID
from backend.new_core.chroma_repository import ChromaRepository


__all__ = ["ChromaCatalog"]


class ChromaCatalog:
    """Loads and edits chroma catalog rows."""

    def __init__(self, chroma: ChromaRepository) -> None:
        """Remembers the chroma store.

        :param chroma: the chroma repository.
        """
        self._chroma = chroma

    def chroma_rows(self) -> tuple[Chroma, ...]:
        """Returns every stored chroma row with a non-empty name.

        :return: the tuple[Chroma, ...] result.
        """
        named = (
            row
            for row in self._chroma.take_all()
            if row.name != ""
        )
        return named

    def chroma_row(self, chroma_id: ChromaID) -> Chroma:
        """Returns one chroma row.

        :param chroma_id: id of the chroma row.

        :raises KeyError: if there is no row.

        :return: the Chroma result.
        """
        return self._chroma.take(chroma_id)

    def create_chroma(
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

        :return: the ChromaID result.
        """
        return self._chroma.add(name, cyan, magenta, yellow, black)

    def replace_chroma(self, chroma: Chroma) -> None:
        """Overwrites non-id fields of an existing row.

        :param chroma:

        :raises KeyError: if there is no row with this id.
        """
        self._chroma.replace(chroma)

    def delete_chroma(self, chroma_id: ChromaID) -> None:
        """Removes a chroma row.

        :param chroma_id:

        :raises KeyError: if there is no row.
        """
        self._chroma.delete(chroma_id)