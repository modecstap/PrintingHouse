"""Parts and polymorphic operation subtype rows."""

from sqlalchemy import ForeignKey, Identity, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.schema import Base


class PartRow(Base):
    __tablename__ = "parts"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    count: Mapped[int] = mapped_column(Integer)
    markup: Mapped[int] = mapped_column(Integer)
    target_name: Mapped[str] = mapped_column(Text)
    target_height: Mapped[int] = mapped_column(Integer)
    target_width: Mapped[int] = mapped_column(Integer)
    sheet_id: Mapped[int] = mapped_column(ForeignKey("sheets.id"))
    bleeds: Mapped[int] = mapped_column(Integer)
    spacing: Mapped[int] = mapped_column(Integer)


class PartOperationRow(Base):
    __tablename__ = "part_operations"
    __table_args__ = (UniqueConstraint("part_id", "position"),)

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    part_id: Mapped[int] = mapped_column(
        ForeignKey("parts.id", ondelete="CASCADE"),
    )
    position: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(16))


class PartPrintRow(Base):
    __tablename__ = "part_prints"

    operation_id: Mapped[int] = mapped_column(
        ForeignKey("part_operations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    printer_id: Mapped[int] = mapped_column(ForeignKey("printers.id"))
    operator_id: Mapped[int] = mapped_column(ForeignKey("press_operators.id"))
    chroma: Mapped[str] = mapped_column(Text)


class PartLaminateRow(Base):
    __tablename__ = "part_laminates"

    operation_id: Mapped[int] = mapped_column(
        ForeignKey("part_operations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    laminator_id: Mapped[int] = mapped_column(ForeignKey("laminators.id"))
    operator_id: Mapped[int] = mapped_column(ForeignKey("laminator_operators.id"))
    lamination: Mapped[str] = mapped_column(Text)
    film_id: Mapped[int] = mapped_column(ForeignKey("films.id"))


class PartCutRow(Base):
    __tablename__ = "part_cuts"

    operation_id: Mapped[int] = mapped_column(
        ForeignKey("part_operations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    cutter_id: Mapped[int] = mapped_column(ForeignKey("cutters.id"))
    operator_id: Mapped[int] = mapped_column(ForeignKey("cutter_operators.id"))


class PartDieCutRow(Base):
    __tablename__ = "part_die_cuts"

    operation_id: Mapped[int] = mapped_column(
        ForeignKey("part_operations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    operator_id: Mapped[int] = mapped_column(ForeignKey("die_cutter_operators.id"))

