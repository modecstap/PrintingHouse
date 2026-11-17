"""SQL implementation of ``ChromaRepository``."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.new_core.chroma import Chroma, ChromaID
from backend.new_core.values.percent import Percent
from backend.storage.chroma.tables import ChromaRow


__all__ = ["SqlChromaRepository"]


class SqlChromaRepository:
    """Loads and stores chroma rows in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        """Initializes this instance.

        :param session: database session.
        """
        self._session = session

    def take(self, chroma_id: ChromaID) -> Chroma:
        """Returns the chroma row with this id.

        :param chroma_id: id of the chroma row.

        :raises KeyError: if there is no row.

        :return: the Chroma result.
        """
        row = self._session.get(ChromaRow, chroma_id.value)
        if row is None:
            raise KeyError(chroma_id)
        return self._chroma_from_row(chroma_id, row)

    def take_all(self) -> tuple[Chroma, ...]:
        """Returns every stored chroma row.

        :return: the tuple[Chroma, ...] result.
        """
        stmt = select(ChromaRow).order_by(ChromaRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            self._chroma_from_row(ChromaID(row.id), row) for row in rows
        )

    def add(
        self,
        name: str,
        cyan: int,
        magenta: int,
        yellow: int,
        black: int,
    ) -> ChromaID:
        """Inserts a new row; the database assigns the id.

        :param name: the name.
        :param cyan: cyan fill percent.
        :param magenta: magenta fill percent.
        :param yellow: yellow fill percent.
        :param black: black fill percent.

        :return: the ChromaID result.
        """
        Chroma(
            id=ChromaID(0),
            name=name,
            cyan=Percent(cyan),
            magenta=Percent(magenta),
            yellow=Percent(yellow),
            black=Percent(black),
        )
        row = ChromaRow(
            name=name,
            cyan=cyan,
            magenta=magenta,
            yellow=yellow,
            black=black,
        )
        self._session.add(row)
        self._session.flush()
        return ChromaID(row.id)

    def replace(self, chroma: Chroma) -> None:
        """Overwrites non-id fields of an existing row.

        :param chroma:

        :raises KeyError: if there is no row with this id.
        """
        row = self._session.get(ChromaRow, chroma.id.value)
        if row is None:
            raise KeyError(chroma.id)
        row.name = chroma.name
        row.cyan = chroma.cyan.value
        row.magenta = chroma.magenta.value
        row.yellow = chroma.yellow.value
        row.black = chroma.black.value
        self._session.flush()

    def delete(self, chroma_id: ChromaID) -> None:
        """Removes the row with this id.

        :param chroma_id:

        :raises KeyError: if there is no row.
        """
        row = self._session.get(ChromaRow, chroma_id.value)
        if row is None:
            raise KeyError(chroma_id)
        self._session.delete(row)

    def find_or_add(
        self,
        name: str,
        cyan: int,
        magenta: int,
        yellow: int,
        black: int,
    ) -> ChromaID:
        """Returns an existing row matching name and fills or inserts one.

        :param name: the name.
        :param cyan: cyan fill percent.
        :param magenta: magenta fill percent.
        :param yellow: yellow fill percent.
        :param black: black fill percent.

        :return: the ChromaID result.
        """
        stmt = (
            select(ChromaRow)
            .where(
                ChromaRow.name == name,
                ChromaRow.cyan == cyan,
                ChromaRow.magenta == magenta,
                ChromaRow.yellow == yellow,
                ChromaRow.black == black,
            )
            .limit(1)
        )
        row = self._session.execute(stmt).scalars().first()
        if row is not None:
            return ChromaID(row.id)
        return self.add(name, cyan, magenta, yellow, black)

    @staticmethod
    def _chroma_from_row(chroma_id: ChromaID, row: ChromaRow) -> Chroma:
        """Handles chroma from row.

        :param chroma_id: id of the chroma row.
        :param row: the row.

        :return: the Chroma result.
        """
        return Chroma(
            id=chroma_id,
            name=row.name,
            cyan=Percent(row.cyan),
            magenta=Percent(row.magenta),
            yellow=Percent(row.yellow),
            black=Percent(row.black),
        )