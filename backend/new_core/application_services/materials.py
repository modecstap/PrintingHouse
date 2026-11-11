"""Use cases that list, load, create, replace, and remove material catalog rows."""

from __future__ import annotations

from backend.new_core.format import Format
from backend.new_core.materials.film import Film, FilmID
from backend.new_core.materials.film_repository import FilmRepository
from backend.new_core.materials.paper import Paper
from backend.new_core.materials.sheet import Sheet, SheetID
from backend.new_core.materials.sheet_repository import SheetRepository
from backend.new_core.values.money import Money


class MaterialCatalogService:
    """Loads and edits films and sheets."""

    def __init__(
        self,
        films: FilmRepository,
        sheets: SheetRepository,
    ) -> None:
        """Remembers the material stores.

        :param films:
        :param sheets:
        """
        self._films = films
        self._sheets = sheets

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

    def sheets(self) -> tuple[Sheet, ...]:
        """Returns every stored sheet.

        :return: sheets in ascending id order.
        """
        return self._sheets.take_all()

    def sheet(self, sheet_id: SheetID) -> Sheet:
        """Returns one sheet.

        :param sheet_id:

        :raises KeyError: if there is no sheet.

        :return: the sheet row.
        """
        return self._sheets.take(sheet_id)

    def create_sheet(self, paper: Paper, format: Format) -> SheetID:
        """Inserts a new sheet; the store assigns the id.

        :param paper:
        :param format:

        :return: the assigned sheet id.
        """
        return self._sheets.add(paper, format)

    def replace_sheet(self, sheet: Sheet) -> None:
        """Overwrites non-id fields of an existing sheet.

        :param sheet:

        :raises KeyError: if there is no sheet with this id.

        :return: nothing.
        """
        self._sheets.replace(sheet)

    def delete_sheet(self, sheet_id: SheetID) -> None:
        """Removes a sheet.

        :param sheet_id:

        :raises KeyError: if there is no sheet.

        :return: nothing.
        """
        self._sheets.delete(sheet_id)

    def paper_types(self) -> tuple[str, ...]:
        """Returns unique paper type names from stored sheets.

        :return: canonical type strings in ascending order.
        """
        return self._sheets.distinct_paper_types()

    def paper_densities(self) -> tuple[int, ...]:
        """Returns unique paper densities from stored sheets.

        :return: densities in ascending numeric order.
        """
        return self._sheets.distinct_paper_densities()

    def film_densities(self) -> tuple[int, ...]:
        """Returns unique film densities from stored films.

        :return: densities in ascending numeric order.
        """
        return self._films.distinct_film_densities()
