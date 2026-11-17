"""Edges catalog rows."""

from sqlalchemy import Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.base import Base

__all__ = [
    "EdgesRow",
]


class EdgesRow(Base):  # pylint: disable=too-few-public-methods
    """Edges Row.
    """
    __tablename__ = "edges"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    bleeds: Mapped[int] = mapped_column(Integer)
    spacing: Mapped[int] = mapped_column(Integer)