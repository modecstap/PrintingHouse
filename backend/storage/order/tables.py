"""Orders, blocks, and product additional work."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.base import Base

__all__ = [
    "OrderRow",
    "OrderBlockRow",
    "OrderAdditionalWorkRow",
]

_MONEY = Numeric(18, 4)


class OrderRow(Base):  # pylint: disable=too-few-public-methods
    """Order Row.
    """
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    count: Mapped[int] = mapped_column(Integer)
    parts_markup: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0")
    description: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class OrderBlockRow(Base):  # pylint: disable=too-few-public-methods
    """Order Block Row.
    """
    __tablename__ = "order_blocks"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), unique=True)


class OrderAdditionalWorkRow(Base):  # pylint: disable=too-few-public-methods
    """Order Additional Work Row.
    """
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
