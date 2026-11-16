"""Film catalog use cases."""

from __future__ import annotations

from backend.new_core.materials.film import Film, FilmID
from backend.new_core.materials.film_repository import FilmRepository
from backend.new_core.values.money import Money


__all__ = ["FilmCatalog"]

class FilmCatalog:
    """Loads and edits films."""

    def __init__(self, films: FilmRepository) -> None:
        """Remembers the film store.

        :param films: the films.
        """
        self._films = films

    def films(self) -> tuple[Film, ...]:
        """Returns every stored film.

        :return: the tuple[Film, ...] result.
        """
        return self._films.take_all()

    def film(self, film_id: FilmID) -> Film:
        """Returns one film.

        :param film_id: id of the film.

        :raises KeyError: if there is no film.

        :return: the Film result.
        """
        return self._films.take(film_id)

    def create_film(self, name: str, price: Money, density: int) -> FilmID:
        """Inserts a new film; the store assigns the id.

        :param name: the name.
        :param price: the price.
        :param density: the density.

        :return: the FilmID result.
        """
        return self._films.add(name, price, density)

    def replace_film(self, film: Film) -> None:
        """Overwrites non-id fields of an existing film.

        :param film:

        :raises KeyError: if there is no film with this id.
        """
        self._films.replace(film)

    def delete_film(self, film_id: FilmID) -> None:
        """Removes a film.

        :param film_id:

        :raises KeyError: if there is no film.
        """
        self._films.delete(film_id)

    def film_densities(self) -> tuple[int, ...]:
        """Returns unique film densities from stored films.

        :return: the tuple[int, ...] result.
        """
        return self._films.distinct_film_densities()
