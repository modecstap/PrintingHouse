"""Films and press sheets."""

from decimal import Decimal

from sqlalchemy import Identity, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.schema import Base

_MONEY = Numeric(18, 4)


class FilmRow(Base):
    __tablename__ = "films"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(_MONEY)
    density: Mapped[int] = mapped_column(Integer)


class SheetRow(Base):
    __tablename__ = "sheets"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    paper_density: Mapped[int] = mapped_column(Integer)
    paper_thickness: Mapped[int] = mapped_column(Integer)
    paper_name: Mapped[str] = mapped_column(Text)
    paper_price_per_kilo: Mapped[Decimal] = mapped_column(_MONEY)
    format_name: Mapped[str] = mapped_column(Text)
    format_height: Mapped[int] = mapped_column(Integer)
    format_width: Mapped[int] = mapped_column(Integer)
