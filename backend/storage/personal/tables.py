"""Press, laminate, cut, and die-cut operators."""

from decimal import Decimal

from sqlalchemy import Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.base import Base

_MONEY = Numeric(18, 4)


class PressOperatorRow(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "press_operators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    salary_by_operation: Mapped[Decimal] = mapped_column(_MONEY)


class LaminatorOperatorRow(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "laminator_operators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    salary_by_operation: Mapped[Decimal] = mapped_column(_MONEY)


class CutterOperatorRow(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "cutter_operators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    salary_by_operation: Mapped[Decimal] = mapped_column(_MONEY)


class DieCutterOperatorRow(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "die_cutter_operators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    salary_by_operation: Mapped[Decimal] = mapped_column(_MONEY)

