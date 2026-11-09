"""Print runs and per-order id counters."""

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.schema import Base


class PrintRunRow(Base):
    __tablename__ = "print_runs"
    __table_args__ = (UniqueConstraint("order_id", "position"),)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        primary_key=True,
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    position: Mapped[int] = mapped_column(Integer)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), unique=True)
    required_count: Mapped[int] = mapped_column(Integer)


class PrintRunIdCounterRow(Base):
    __tablename__ = "print_run_id_counters"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    next_value: Mapped[int] = mapped_column(Integer)

