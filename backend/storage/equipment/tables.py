"""Printers, laminators, and cutters."""

from decimal import Decimal

from sqlalchemy import Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.schema import Base

_MONEY = Numeric(18, 4)


class PrinterRow(Base):
    __tablename__ = "printers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    startup: Mapped[Decimal] = mapped_column(_MONEY)
    cyan: Mapped[Decimal] = mapped_column(_MONEY)
    magenta: Mapped[Decimal] = mapped_column(_MONEY)
    yellow: Mapped[Decimal] = mapped_column(_MONEY)
    black: Mapped[Decimal] = mapped_column(_MONEY)


class LaminatorRow(Base):
    __tablename__ = "laminators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    startup: Mapped[Decimal] = mapped_column(_MONEY)


class CutterRow(Base):
    __tablename__ = "cutters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    max_stack: Mapped[int] = mapped_column(Integer)

