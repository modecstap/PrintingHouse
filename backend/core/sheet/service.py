from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.core.sheet.format import SheetFormat, standard_formats
from backend.core.sheet.repository import (
    SheetRepository,
    SheetSizeRejected,
)
from backend.core.sheet.sheet import Sheet


@dataclass(frozen=True)
class SaveSheet:
    """Saves one sheet. The command has no name."""

    id: int | None
    height: int
    width: int
    density: int
    cost: Money


def _factory_format(height: int, width: int) -> SheetFormat | None:
    for item in standard_formats():
        if item.height == height and item.width == width:
            return item
    return None


class SheetService:
    def __init__(self, sheets: SheetRepository) -> None:
        """Remembers the sheet repository.

        :param sheets:
        """
        self._sheets = sheets

    def save(self, command: SaveSheet) -> int:
        """Inserts a factory sheet or reprices a stored one.

        :param command: an empty id inserts. An id reprices that row.
        Height and width on an existing id are ignored. The name is
        not part of the command.

        :raises SheetSizeRejected: if an empty id has a height and width
        that are not one factory format. The catalog is unchanged.
        :raises SheetNotFound: if the id has no row.
        :raises SheetVersionConflict: if the stored version changes
        before the reprice is written. The row is left unchanged.
        :raises SheetStoreUnavailable: if there is no connection to the database.

        :return: the id to keep. A new format is stored under the factory
        name. The same height, width, density, and cost returns the row
        already stored, including a moved row, and does not change it.
        A reprice that matches another row returns that row's id and
        changes neither row. A reprice that matches no row writes the
        density and the rate and increases version.
        """
        sheet_id = command.id
        if sheet_id is None:
            return self._save_new(command)
        return self._save_existing(command, sheet_id)

    def _save_new(self, command: SaveSheet) -> int:
        chosen = _factory_format(command.height, command.width)
        if chosen is None:
            raise SheetSizeRejected()
        stored = self._sheets.find_same(
            chosen.height, chosen.width, command.density, command.cost
        )
        if stored is not None and stored.id is not None:
            return stored.id
        return self._sheets.save(
            Sheet(chosen, command.density, command.cost)
        )

    def _save_existing(self, command: SaveSheet, sheet_id: int) -> int:
        sheet = self._sheets.take(sheet_id)
        stored = self._sheets.find_same(
            sheet.format.height,
            sheet.format.width,
            command.density,
            command.cost,
        )
        if stored is not None and stored.id is not None:
            return stored.id
        sheet.reprice(command.density, command.cost)
        return self._sheets.save(sheet)

    def take_all(self) -> list[Sheet]:
        """Returns every sheet.

        :raises SheetStoreUnavailable: if there is no connection to the database.

        :return: each sheet once, by ascending id. No rows: an empty list.
        """
        return self._sheets.take_all()

    def delete(self, sheet_id: int) -> None:
        """Deletes this sheet, or raises when the row is missing or still used.

        :param sheet_id:

        :raises SheetNotFound: if there is no row.
        :raises SheetInUse: if a printing row or a printing in the reference
        document points at this id. The row and those references stay.
        :raises SheetStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        self._sheets.delete(sheet_id)
