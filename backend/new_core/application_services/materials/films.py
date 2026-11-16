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

        :param films:
        """
        self._films = films

    def films(self) -> tuple[Film, ...]:
        """Returns every stored film.

        :return: films in ascending id order.
        """
        return self._films.take_all()

    def film(self, film_id: FilmID) -> Film:
        """Returns one film.

        :param film_id:

        :raises KeyError: if there is no film.

        :return: the film row.
        """
        return self._films.take(film_id)

    def create_film(self, name: str, price: Money, density: int) -> FilmID:
        """Inserts a new film; the store assigns the id.

        :param name:
        :param price:
        :param density:

        :return: the assigned film id.
        """
        return self._films.add(name, price, density)

    def replace_film(self, film: Film) -> None:
        """Overwrites non-id fields of an existing film.

        :param film:

        :raises KeyError: if there is no film with this id.

        :return: nothing.
        """
        self._films.replace(film)

    def delete_film(self, film_id: FilmID) -> None:
        """Removes a film.

        :param film_id:

        :raises KeyError: if there is no film.

        :return: nothing.
        """
        self._films.delete(film_id)

    def film_densities(self) -> tuple[int, ...]:
        """Returns unique film densities from stored films.

        :return: densities in ascending numeric order.
        """
        return self._films.distinct_film_densities()
