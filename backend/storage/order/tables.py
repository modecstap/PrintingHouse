"""Orders, blocks, and product additional work."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.schema import Base

_MONEY = Numeric(18, 4)


class OrderRow(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    count: Mapped[int] = mapped_column(Integer)


class OrderBlockRow(Base):
    __tablename__ = "order_blocks"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), unique=True)


class OrderAdditionalWorkRow(Base):
    __tablename__ = "order_additional_works"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(_MONEY)
    description: Mapped[str] = mapped_column(Text)
    markup: Mapped[int] = mapped_column(Integer)

