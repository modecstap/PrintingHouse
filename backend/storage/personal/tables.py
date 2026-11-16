"""Press, laminate, cut, and die-cut operators."""

from decimal import Decimal

from sqlalchemy import Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.base import Base

__all__ = [
    "PressOperatorRow",
    "LaminatorOperatorRow",
    "CutterOperatorRow",
    "DieCutterOperatorRow",
]

_MONEY = Numeric(18, 4)


class PressOperatorRow(Base):  # pylint: disable=too-few-public-methods
    """Press Operator Row.
    """
    __tablename__ = "press_operators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    salary_by_operation: Mapped[Decimal] = mapped_column(_MONEY)


class LaminatorOperatorRow(Base):  # pylint: disable=too-few-public-methods
    """Laminator Operator Row.
    """
    __tablename__ = "laminator_operators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    salary_by_operation: Mapped[Decimal] = mapped_column(_MONEY)


class CutterOperatorRow(Base):  # pylint: disable=too-few-public-methods
    """Cutter Operator Row.
    """
    __tablename__ = "cutter_operators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    salary_by_operation: Mapped[Decimal] = mapped_column(_MONEY)


class DieCutterOperatorRow(Base):  # pylint: disable=too-few-public-methods
    """Die Cutter Operator Row.
    """
    __tablename__ = "die_cutter_operators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    salary_by_operation: Mapped[Decimal] = mapped_column(_MONEY)
