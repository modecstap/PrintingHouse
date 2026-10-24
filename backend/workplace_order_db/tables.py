from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class WorkplaceOrderRow(Base):
    __tablename__ = "workplace_order"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    unit_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    markup: Mapped[Decimal] = mapped_column(Numeric, nullable=False)


class OperationCostRow(Base):
    __tablename__ = "workplace_operation_cost"
    __table_args__ = (UniqueConstraint("order_id", "position"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("workplace_order.id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)


class PrintingRow(Base):
    __tablename__ = "workplace_printing"
    __table_args__ = (UniqueConstraint("order_id", "position"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("workplace_order.id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sheet_by_fitting: Mapped[int] = mapped_column(BigInteger, nullable=False)
    stack_height: Mapped[int] = mapped_column(BigInteger, nullable=False)
    press_sheet_density: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )
    press_sheet_width: Mapped[int] = mapped_column(BigInteger, nullable=False)
    press_sheet_height: Mapped[int] = mapped_column(BigInteger, nullable=False)
    press_sheet_spacing: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )
    list_width: Mapped[int] = mapped_column(BigInteger, nullable=False)
    list_height: Mapped[int] = mapped_column(BigInteger, nullable=False)
    list_bleeds: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chroma: Mapped[str] = mapped_column(String(64), nullable=False)
    lamination: Mapped[str] = mapped_column(String(64), nullable=False)
    die_cutting: Mapped[bool] = mapped_column(Boolean, nullable=False)
    press_cyan: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    press_magenta: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    press_yellow: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    press_black: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    press_paper: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    press_salary: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    cut_salary: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    lamination_startup: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    lamination_film_cost: Mapped[Decimal] = mapped_column(
        Numeric, nullable=False
    )
    lamination_salary: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    die_cut_salary: Mapped[Decimal] = mapped_column(Numeric, nullable=False)


class CostReportRow(Base):
    __tablename__ = "workplace_cost_report"
    __table_args__ = (UniqueConstraint("order_id", "position"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("workplace_order.id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost_price: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    edition_cost: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    profit_after_tax: Mapped[Decimal] = mapped_column(Numeric, nullable=False)


class PrintingCostRow(Base):
    __tablename__ = "workplace_printing_cost"
    __table_args__ = (UniqueConstraint("cost_report_id", "position"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    cost_report_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("workplace_cost_report.id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    items_per_sheet: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sheet_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    unit_cost_price: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    edition_cost_price: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    edition_cost: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    profit_before_tax: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    profit_after_tax: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
