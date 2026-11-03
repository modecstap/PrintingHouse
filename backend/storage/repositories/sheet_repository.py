from collections.abc import Callable
from decimal import Decimal
from typing import TypeVar

from sqlalchemy import select, update
from sqlalchemy.engine import Engine
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError, InterfaceError, OperationalError
from sqlalchemy.orm import Session

from backend.core.accountant.money import Money
from backend.core.sheet.format import SheetFormat
from backend.core.sheet.repository import (
    SheetInUse,
    SheetNotFound,
    SheetOperation,
    SheetRepository,
    SheetStoreUnavailable,
    SheetVersionConflict,
)
from backend.core.sheet.sheet import Sheet
from backend.storage.tables.sheet import SheetRow
from backend.storage.tables.workplace_order import (
    PrintingRow,
    WorkplaceReferenceRow,
)

_T = TypeVar("_T")
_SHEET_FK = "printing_sheet_id_fkey"


def _decimal(value: object) -> Decimal:
    # Money принимает только объект, у которого type is Decimal.
    if type(value) is Decimal:
        return value
    return Decimal(str(value))


def _sheet_from_row(row: SheetRow) -> Sheet:
    sheet = Sheet(
        SheetFormat(row.name, int(row.height), int(row.width)),
        int(row.density),
        Money(_decimal(row.cost)),
    )
    sheet.id = int(row.id)
    sheet.version = int(row.version)
    return sheet


def _constraint_name(error: IntegrityError) -> str | None:
    diag = getattr(error.orig, "diag", None)
    name = getattr(diag, "constraint_name", None)
    if type(name) is str:
        return name
    return None


def _is_printing_sheet_fk(error: IntegrityError) -> bool:
    return _constraint_name(error) == _SHEET_FK


def _is_new_tuple_conflict(error: IntegrityError) -> bool:
    orig = error.orig
    if isinstance(orig, UniqueViolation):
        return True
    return getattr(orig, "sqlstate", None) == "23505"


def _reference_uses_sheet(session: Session, sheet_id: int) -> bool:
    row = session.get(WorkplaceReferenceRow, 1, with_for_update=True)
    if row is None:
        return False
    document = row.document
    if type(document) is not dict:
        return False
    printings = document.get("printings")
    if type(printings) is not list:
        return False
    for item in printings:
        if type(item) is not dict:
            continue
        press_sheet = item.get("press_sheet")
        if type(press_sheet) is int and press_sheet == sheet_id:
            return True
    return False


def _sheet_in_use(session: Session, sheet_id: int) -> bool:
    linked = session.scalar(
        select(PrintingRow.id)
        .where(PrintingRow.sheet_id == sheet_id)
        .limit(1)
    )
    return linked is not None or _reference_uses_sheet(session, sheet_id)


class SqlSheetRepository(SheetRepository):
    def __init__(self, engine: Engine) -> None:
        """Remembers the Engine.

        :param engine:
        """
        self._engine = engine

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
        try:
            return self._call(
                "save",
                sheet.id,
                lambda session: self._save(session, sheet),
            )
        except IntegrityError as error:
            # Две вставки одной четвёрки: индекс отклоняет вторую.
            # Проигравшая транзакция уже откатилась, строка победителя на месте.
            if sheet.id is not None or not _is_new_tuple_conflict(error):
                raise
            stored = self.find_same(
                sheet.format.height,
                sheet.format.width,
                sheet.density,
                sheet.cost,
            )
            if stored is None or stored.id is None:
                raise
            return stored.id

    def take(self, sheet_id: int) -> Sheet:
        """Returns the whole sheet with this id.

        :param sheet_id:

        :raises SheetNotFound: if there is no row.
        :raises SheetStoreUnavailable: if there is no connection to the database.

        :return: the sheet, including version, format, density, and cost.
        """
        return self._call(
            "take",
            sheet_id,
            lambda session: self._take(session, sheet_id),
        )

    def take_all(self) -> list[Sheet]:
        """Returns every sheet.

        :raises SheetStoreUnavailable: if there is no connection to the database.

        :return: each sheet once, by ascending id. No rows: an empty list.
        """
        return self._call(
            "take_all",
            None,
            lambda session: self._take_all(session),
        )

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
        return self._call(
            "find_same",
            None,
            lambda session: self._find_same(
                session, height, width, density, cost
            ),
        )

    def delete(self, sheet_id: int) -> None:
        """Deletes this sheet, or raises when the row is missing or still used.

        :param sheet_id:

        :raises SheetNotFound: if there is no row.
        :raises SheetInUse: if a printing row or a printing in the reference
        document points at this id. The row and those references stay.
        :raises SheetStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        self._call(
            "delete",
            sheet_id,
            lambda session: self._delete(session, sheet_id),
        )

    def _call(
        self,
        operation: SheetOperation,
        sheet_id: int | None,
        action: Callable[[Session], _T],
    ) -> _T:
        try:
            with Session(self._engine) as session:
                with session.begin():
                    return action(session)
        except (OperationalError, InterfaceError) as error:
            raise SheetStoreUnavailable(operation, sheet_id) from error

    def _save(self, session: Session, sheet: Sheet) -> int:
        sheet_id = sheet.id
        if sheet_id is None:
            return self._insert(session, sheet)
        return self._update(session, sheet, sheet_id)

    def _insert(self, session: Session, sheet: Sheet) -> int:
        row = SheetRow(
            version=0,
            name=sheet.format.name,
            height=sheet.format.height,
            width=sheet.format.width,
            density=sheet.density,
            cost=sheet.cost.amount,
        )
        session.add(row)
        session.flush()
        return int(row.id)

    def _update(self, session: Session, sheet: Sheet, sheet_id: int) -> int:
        updated_id = session.scalar(
            update(SheetRow)
            .where(
                SheetRow.id == sheet_id,
                SheetRow.version == sheet.version,
            )
            .values(
                density=sheet.density,
                cost=sheet.cost.amount,
                version=SheetRow.version + 1,
            )
            .returning(SheetRow.id)
        )
        if updated_id is not None:
            return int(updated_id)
        if session.get(SheetRow, sheet_id) is None:
            raise SheetNotFound("save", sheet_id)
        raise SheetVersionConflict(sheet_id)

    def _take(self, session: Session, sheet_id: int) -> Sheet:
        row = session.get(SheetRow, sheet_id)
        if row is None:
            raise SheetNotFound("take", sheet_id)
        return _sheet_from_row(row)

    def _take_all(self, session: Session) -> list[Sheet]:
        rows = session.scalars(
            select(SheetRow).order_by(SheetRow.id.asc())
        ).all()
        return [_sheet_from_row(row) for row in rows]

    def _find_same(
        self,
        session: Session,
        height: int,
        width: int,
        density: int,
        cost: Money,
    ) -> Sheet | None:
        row = session.scalar(
            select(SheetRow).where(
                SheetRow.height == height,
                SheetRow.width == width,
                SheetRow.density == density,
                SheetRow.cost == cost.amount,
            )
        )
        if row is None:
            return None
        return _sheet_from_row(row)

    def _delete(self, session: Session, sheet_id: int) -> None:
        row = session.get(SheetRow, sheet_id, with_for_update=True)
        if row is None:
            raise SheetNotFound("delete", sheet_id)
        if _sheet_in_use(session, sheet_id):
            raise SheetInUse(sheet_id)
        session.delete(row)
        try:
            session.flush()
        except IntegrityError as error:
            # Вставка печати могла занять лист после проверки.
            if _is_printing_sheet_fk(error):
                raise SheetInUse(sheet_id) from error
            raise
