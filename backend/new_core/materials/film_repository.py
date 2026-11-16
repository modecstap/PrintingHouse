"""Film catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.materials.film import Film, FilmID
from backend.new_core.values.money import Money


__all__ = ["FilmRepository"]

class FilmRepository(Protocol):
    """Loads and stores films by id."""

    def take(self, film_id: FilmID) -> Film:
        """Returns the film with this id.

        :param film_id: id of the film.

        :raises KeyError: if there is no film.
"""
        ...

    def take_all(self) -> tuple[Film, ...]:
        """Returns every stored film.
"""
        ...

    def add(self, name: str, price: Money, density: int) -> FilmID:
        """Inserts a new film; the store assigns the id.

        :param name: the name.
        :param price: the price.
        :param density: the density.
"""
        ...

    def replace(self, film: Film) -> None:
        """Overwrites non-id fields of an existing film.

        :param film:

        :raises KeyError: if there is no film with this id.
        """
        ...

    def delete(self, film_id: FilmID) -> None:
        """Removes the film with this id.

        :param film_id:

        :raises KeyError: if there is no film.
        """
        ...

    def distinct_film_densities(self) -> tuple[int, ...]:
        """Returns unique film densities across stored films.
"""
        ...
