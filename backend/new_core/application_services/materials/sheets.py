"""Sheet catalog use cases."""

from __future__ import annotations

from backend.new_core.format import Format
from backend.new_core.materials.paper import Paper
from backend.new_core.materials.sheet import Sheet, SheetID
from backend.new_core.materials.sheet_repository import SheetRepository


class SheetCatalog:
    """Loads and edits sheets."""

    def __init__(self, sheets: SheetRepository) -> None:
        """Remembers the sheet store.

        :param sheets:
        """
        self._sheets = sheets

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

    def create_sheet(self, paper: Paper, sheet_format: Format) -> SheetID:
        """Inserts a new sheet; the store assigns the id.

        :param paper:
        :param sheet_format:

        :return: the assigned sheet id.
        """
        return self._sheets.add(paper, sheet_format)

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
