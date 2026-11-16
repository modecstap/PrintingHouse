"""Sheet catalog use cases."""

from __future__ import annotations

from backend.new_core.format import Format
from backend.new_core.materials.paper import Paper
from backend.new_core.materials.sheet import Sheet, SheetID
from backend.new_core.materials.sheet_repository import SheetRepository


__all__ = ["SheetCatalog"]

class SheetCatalog:
    """Loads and edits sheets."""

    def __init__(self, sheets: SheetRepository) -> None:
        """Remembers the sheet store.

        :param sheets: the sheets.
        """
        self._sheets = sheets

    def sheets(self) -> tuple[Sheet, ...]:
        """Returns every stored sheet.

        :return: the tuple[Sheet, ...] result.
        """
        return self._sheets.take_all()

    def sheet(self, sheet_id: SheetID) -> Sheet:
        """Returns one sheet.

        :param sheet_id: id of the sheet.

        :raises KeyError: if there is no sheet.

        :return: the Sheet result.
        """
        return self._sheets.take(sheet_id)

    def create_sheet(self, paper: Paper, sheet_format: Format) -> SheetID:
        """Inserts a new sheet; the store assigns the id.

        :param paper: the paper.
        :param sheet_format: the sheet format.

        :return: the SheetID result.
        """
        return self._sheets.add(paper, sheet_format)

    def replace_sheet(self, sheet: Sheet) -> None:
        """Overwrites non-id fields of an existing sheet.

        :param sheet:

        :raises KeyError: if there is no sheet with this id.
        """
        self._sheets.replace(sheet)

    def delete_sheet(self, sheet_id: SheetID) -> None:
        """Removes a sheet.

        :param sheet_id:

        :raises KeyError: if there is no sheet.
        """
        self._sheets.delete(sheet_id)

    def paper_types(self) -> tuple[str, ...]:
        """Returns unique paper type names from stored sheets.

        :return: the tuple[str, ...] result.
        """
        return self._sheets.distinct_paper_types()

    def paper_densities(self) -> tuple[int, ...]:
        """Returns unique paper densities from stored sheets.

        :return: the tuple[int, ...] result.
        """
        return self._sheets.distinct_paper_densities()
