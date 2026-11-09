"""SQL implementation of ``FilmRepository``."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.new_core.materials.film import Film, FilmID
from backend.new_core.values.money import Money
from backend.storage.materials.tables import FilmRow


class SqlFilmRepository:
    """Loads and stores films in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, film_id: FilmID) -> Film:
        """Returns the film with this id.

        :param film_id:

        :raises KeyError: if there is no film.

        :return: the film row.
        """
        row = self._session.get(FilmRow, film_id.value)
        if row is None:
            raise KeyError(film_id)
        return self._film_from_row(film_id, row)

    def take_all(self) -> tuple[Film, ...]:
        """Returns every stored film.

        :return: films in ascending id order.
        """
        stmt = select(FilmRow).order_by(FilmRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(self._film_from_row(FilmID(row.id), row) for row in rows)

    def add(self, name: str, price: Money, density: int) -> FilmID:
        """Inserts a new film; the database assigns the id.

        :param name:
        :param price:
        :param density:

        :return: the assigned film id.
        """
        row = FilmRow(
            name=name,
            price=price.amount,
            density=density,
        )
        self._session.add(row)
        self._session.flush()
        return FilmID(row.id)

    def replace(self, film: Film) -> None:
        """Overwrites non-id fields of an existing film.

        :param film:

        :raises KeyError: if there is no film with this id.

        :return: nothing.
        """
        row = self._session.get(FilmRow, film.id.value)
        if row is None:
            raise KeyError(film.id)
        row.name = film.name
        row.price = film.price.amount
        row.density = film.density
        self._session.flush()

    def delete(self, film_id: FilmID) -> None:
        """Removes the film with this id.

        :param film_id:

        :raises KeyError: if there is no film.

        :return: nothing.
        """
        row = self._session.get(FilmRow, film_id.value)
        if row is None:
            raise KeyError(film_id)
        self._session.delete(row)

    @staticmethod
    def _film_from_row(film_id: FilmID, row: FilmRow) -> Film:
        return Film(
            id=film_id,
            name=row.name,
            price=Money(row.price),
            density=row.density,
        )
