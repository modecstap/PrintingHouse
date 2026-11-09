"""SQL implementation of ``SheetRepository``."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.new_core.format import Format
from backend.new_core.materials.paper import Paper
from backend.new_core.materials.sheet import Sheet, SheetID
from backend.new_core.values.money import Money
from backend.storage.materials.tables import SheetRow


class SqlSheetRepository:
    """Loads and stores sheets in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, sheet_id: SheetID) -> Sheet:
        """Returns the sheet with this id.

        :param sheet_id:

        :raises KeyError: if there is no sheet.

        :return: the sheet row.
        """
        row = self._session.get(SheetRow, sheet_id.value)
        if row is None:
            raise KeyError(sheet_id)
        return self._sheet_from_row(sheet_id, row)

    def take_all(self) -> tuple[Sheet, ...]:
        """Returns every stored sheet.

        :return: sheets in ascending id order.
        """
        stmt = select(SheetRow).order_by(SheetRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(self._sheet_from_row(SheetID(row.id), row) for row in rows)

    def add(self, paper: Paper, format: Format) -> SheetID:
        """Inserts a new sheet; the database assigns the id.

        :param paper:
        :param format:

        :return: the assigned sheet id.
        """
        row = SheetRow(
            paper_density=paper.density,
            paper_thickness=paper.thickness,
            paper_name=paper.name,
            paper_price_per_kilo=paper.price_per_kilo.amount,
            format_name=format.name,
            format_height=format.height,
            format_width=format.width,
        )
        self._session.add(row)
        self._session.flush()
        return SheetID(row.id)

    def replace(self, sheet: Sheet) -> None:
        """Overwrites non-id fields of an existing sheet.

        :param sheet:

        :raises KeyError: if there is no sheet with this id.

        :return: nothing.
        """
        row = self._session.get(SheetRow, sheet.id.value)
        if row is None:
            raise KeyError(sheet.id)
        row.paper_density = sheet.paper.density
        row.paper_thickness = sheet.paper.thickness
        row.paper_name = sheet.paper.name
        row.paper_price_per_kilo = sheet.paper.price_per_kilo.amount
        row.format_name = sheet.format.name
        row.format_height = sheet.format.height
        row.format_width = sheet.format.width
        self._session.flush()

    def delete(self, sheet_id: SheetID) -> None:
        """Removes the sheet with this id.

        :param sheet_id:

        :raises KeyError: if there is no sheet.

        :return: nothing.
        """
        row = self._session.get(SheetRow, sheet_id.value)
        if row is None:
            raise KeyError(sheet_id)
        self._session.delete(row)

    @staticmethod
    def _sheet_from_row(sheet_id: SheetID, row: SheetRow) -> Sheet:
        return Sheet(
            id=sheet_id,
            paper=Paper(
                density=row.paper_density,
                thickness=row.paper_thickness,
                name=row.paper_name,
                price_per_kilo=Money(row.paper_price_per_kilo),
            ),
            format=Format(
                name=row.format_name,
                height=row.format_height,
                width=row.format_width,
            ),
        )
