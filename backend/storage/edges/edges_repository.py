"""SQL implementation of ``EdgesRepository``."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.new_core.edges import Edges, EdgesID
from backend.storage.edges.tables import EdgesRow


__all__ = ["SqlEdgesRepository"]


class SqlEdgesRepository:
    """Loads and stores edges rows in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        """Initializes this instance.

        :param session: database session.
        """
        self._session = session

    def take(self, edges_id: EdgesID) -> Edges:
        """Returns the edges row with this id.

        :param edges_id: id of the edges row.

        :raises KeyError: if there is no row.

        :return: the Edges result.
        """
        row = self._session.get(EdgesRow, edges_id.value)
        if row is None:
            raise KeyError(edges_id)
        return self._edges_from_row(edges_id, row)

    def take_all(self) -> tuple[Edges, ...]:
        """Returns every stored edges row.

        :return: the tuple[Edges, ...] result.
        """
        stmt = select(EdgesRow).order_by(EdgesRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            self._edges_from_row(EdgesID(row.id), row) for row in rows
        )

    def add(self, name: str, bleeds: int, spacing: int) -> EdgesID:
        """Inserts a new row; the database assigns the id.

        :param name: the name.
        :param bleeds: the bleeds.
        :param spacing: the spacing.

        :return: the EdgesID result.
        """
        Edges(id=EdgesID(0), name=name, bleeds=bleeds, spacing=spacing)
        row = EdgesRow(name=name, bleeds=bleeds, spacing=spacing)
        self._session.add(row)
        self._session.flush()
        return EdgesID(row.id)

    def replace(self, edges: Edges) -> None:
        """Overwrites non-id fields of an existing row.

        :param edges:

        :raises KeyError: if there is no row with this id.
        """
        row = self._session.get(EdgesRow, edges.id.value)
        if row is None:
            raise KeyError(edges.id)
        row.name = edges.name
        row.bleeds = edges.bleeds
        row.spacing = edges.spacing
        self._session.flush()

    def delete(self, edges_id: EdgesID) -> None:
        """Removes the row with this id.

        :param edges_id:

        :raises KeyError: if there is no row.
        """
        row = self._session.get(EdgesRow, edges_id.value)
        if row is None:
            raise KeyError(edges_id)
        self._session.delete(row)

    def find_or_add(self, name: str, bleeds: int, spacing: int) -> EdgesID:
        """Returns an existing row matching name/bleeds/spacing or inserts one.

        :param name: the name.
        :param bleeds: the bleeds.
        :param spacing: the spacing.

        :return: the EdgesID result.
        """
        stmt = (
            select(EdgesRow)
            .where(
                EdgesRow.name == name,
                EdgesRow.bleeds == bleeds,
                EdgesRow.spacing == spacing,
            )
            .limit(1)
        )
        row = self._session.execute(stmt).scalars().first()
        if row is not None:
            return EdgesID(row.id)
        return self.add(name, bleeds, spacing)

    @staticmethod
    def _edges_from_row(edges_id: EdgesID, row: EdgesRow) -> Edges:
        """Handles edges from row.

        :param edges_id: id of the edges row.
        :param row: the row.

        :return: the Edges result.
        """
        return Edges(
            id=edges_id,
            name=row.name,
            bleeds=row.bleeds,
            spacing=row.spacing,
        )