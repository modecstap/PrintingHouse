from typing import Literal, Protocol

from backend.core.accountant.money import Money
from backend.core.sheet.sheet import Sheet

SheetOperation = Literal["save", "take", "take_all", "find_same", "delete"]


class SheetNotFound(Exception):
    def __init__(self, operation: SheetOperation, sheet_id: int) -> None:
        """Reports that there is no sheet with this id.

        :param operation:
        :param sheet_id:

        :return: the text "{operation}: листа нет, id={sheet_id}".
        """
        super().__init__(f"{operation}: листа нет, id={sheet_id}")


class SheetStoreUnavailable(Exception):
    def __init__(
        self,
        operation: SheetOperation,
        sheet_id: int | None,
    ) -> None:
        """Reports that there is no connection to the database.

        :param operation:
        :param sheet_id: may be None when the break is not about one stored sheet.

        :return: the text "{operation}: нет соединения с базой, id={sheet_id}".
        The text has no driver message, database address, or password.
        """
        super().__init__(
            f"{operation}: нет соединения с базой, id={sheet_id}"
        )


class SheetVersionConflict(Exception):
    def __init__(self, sheet_id: int) -> None:
        """Reports that the stored version differs from this sheet.

        :param sheet_id:

        :return: the text "save: версия листа разошлась, id={sheet_id}".
        """
        super().__init__(f"save: версия листа разошлась, id={sheet_id}")


class SheetInUse(Exception):
    def __init__(self, sheet_id: int) -> None:
        """Reports that an order or the reference still points at this sheet.

        :param sheet_id:

        :return: the text "delete: лист занят, id={sheet_id}".
        """
        super().__init__(f"delete: лист занят, id={sheet_id}")


class SheetSizeRejected(Exception):
    def __init__(self) -> None:
        """Reports that the height and width are not a factory format.

        :return: the text "save: высота и ширина не из фабрики".
        """
        super().__init__("save: высота и ширина не из фабрики")


class SheetIdEmpty(Exception):
    def __init__(self, operation: str) -> None:
        """Reports that the printing has no sheet id.

        :param operation: the caller's operation name. str, because order
        save, set_reference, calculate, accept, and delay pass their own
        names, and those names are not sheet-repository operations.

        :return: the text "{operation}: id листа пустой".
        """
        super().__init__(f"{operation}: id листа пустой")


class SheetRepository(Protocol):
    def save(self, sheet: Sheet) -> int:
        """Inserts a new sheet or updates the density and rate of a stored one.

        :param sheet: an empty id inserts a row with version 0.
        An existing id updates density and cost, and sets version to
        version + 1, when the stored version matches. Height, width,
        and name stay as stored.

        :raises SheetNotFound: if the given id has no row.
        :raises SheetVersionConflict: if the stored version differs.
        The row is left unchanged.
        :raises SheetStoreUnavailable: if there is no connection to the database.

        :return: the id of the saved sheet. A new id comes from the database.
        An existing id is returned unchanged. If the insert loses to a row
        with the same height, width, density, and cost, that stored id is
        returned and the stored row is not changed.
        """
        ...

    def take(self, sheet_id: int) -> Sheet:
        """Returns the whole sheet with this id.

        :param sheet_id:

        :raises SheetNotFound: if there is no row.
        :raises SheetStoreUnavailable: if there is no connection to the database.

        :return: the sheet, including version, format, density, and cost.
        """
        ...

    def take_all(self) -> list[Sheet]:
        """Returns every sheet.

        :raises SheetStoreUnavailable: if there is no connection to the database.

        :return: each sheet once, by ascending id. No rows: an empty list.
        """
        ...

    def find_same(
        self, height: int, width: int, density: int, cost: Money
    ) -> Sheet | None:
        """Returns the sheet with this height, width, density, and rate.

        :param height: compared as given. It is not swapped with width.
        :param width: compared as given. It is not swapped with height.
        :param density:
        :param cost: numeric equality of the rate is enough.

        :raises SheetStoreUnavailable: if there is no connection to the database.

        :return: the matching sheet, including version. No such four-tuple: None.
        The same name does not by itself make two sheets the same.
        """
        ...

    def delete(self, sheet_id: int) -> None:
        """Deletes this sheet, or raises when the row is missing or still used.

        :param sheet_id:

        :raises SheetNotFound: if there is no row.
        :raises SheetInUse: if a printing row or a printing in the reference
        document points at this id. The row and those references stay.
        :raises SheetStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        ...
