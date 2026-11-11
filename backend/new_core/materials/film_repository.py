"""Film catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.materials.film import Film, FilmID
from backend.new_core.values.money import Money


class FilmRepository(Protocol):
    """Loads and stores films by id."""

    def take(self, film_id: FilmID) -> Film:
        """Returns the film with this id.

        :param film_id:

        :raises KeyError: if there is no film.

        :return: the film row.
        """
        ...

    def take_all(self) -> tuple[Film, ...]:
        """Returns every stored film.

        :return: films in ascending id order.
        """
        ...

    def add(self, name: str, price: Money, density: int) -> FilmID:
        """Inserts a new film; the store assigns the id.

        :param name:
        :param price:
        :param density:

        :return: the assigned film id.
        """
        ...

    def replace(self, film: Film) -> None:
        """Overwrites non-id fields of an existing film.

        :param film:

        :raises KeyError: if there is no film with this id.

        :return: nothing.
        """
        ...

    def delete(self, film_id: FilmID) -> None:
        """Removes the film with this id.

        :param film_id:

        :raises KeyError: if there is no film.

        :return: nothing.
        """
        ...

    def distinct_film_densities(self) -> tuple[int, ...]:
        """Returns unique film densities across stored films.

        :return: densities in ascending numeric order.
        """
        ...
