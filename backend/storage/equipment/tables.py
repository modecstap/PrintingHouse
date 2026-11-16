"""Printers, laminators, and cutters."""

from decimal import Decimal

from sqlalchemy import Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.base import Base

__all__ = [
    "PrinterRow",
    "LaminatorRow",
    "CutterRow",
]

_MONEY = Numeric(18, 4)


class PrinterRow(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "printers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    spacing: Mapped[int] = mapped_column(Integer)
    startup: Mapped[Decimal] = mapped_column(_MONEY)
    cyan: Mapped[Decimal] = mapped_column(_MONEY)
    magenta: Mapped[Decimal] = mapped_column(_MONEY)
    yellow: Mapped[Decimal] = mapped_column(_MONEY)
    black: Mapped[Decimal] = mapped_column(_MONEY)


class LaminatorRow(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "laminators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    startup: Mapped[Decimal] = mapped_column(_MONEY)


class CutterRow(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "cutters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    max_stack: Mapped[int] = mapped_column(Integer)
