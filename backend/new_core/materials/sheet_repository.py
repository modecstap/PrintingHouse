"""Sheet catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.format import Format
from backend.new_core.materials.paper import Paper
from backend.new_core.materials.sheet import Sheet, SheetID


class SheetRepository(Protocol):
    """Loads and stores sheets by id."""

    def take(self, sheet_id: SheetID) -> Sheet:
        """Returns the sheet with this id.

        :param sheet_id:

        :raises KeyError: if there is no sheet.

        :return: the sheet row.
        """
        ...

    def take_all(self) -> tuple[Sheet, ...]:
        """Returns every stored sheet.

        :return: sheets in ascending id order.
        """
        ...

    def add(self, paper: Paper, format: Format) -> SheetID:
        """Inserts a new sheet; the store assigns the id.

        :param paper:
        :param format:

        :return: the assigned sheet id.
        """
        ...

    def replace(self, sheet: Sheet) -> None:
        """Overwrites non-id fields of an existing sheet.

        :param sheet:

        :raises KeyError: if there is no sheet with this id.

        :return: nothing.
        """
        ...

    def delete(self, sheet_id: SheetID) -> None:
        """Removes the sheet with this id.

        :param sheet_id:

        :raises KeyError: if there is no sheet.

        :return: nothing.
        """
        ...

    def distinct_paper_types(self) -> tuple[str, ...]:
        """Returns unique paper type names across stored sheets.

        :return: canonical type strings in ascending order.
        """
        ...
