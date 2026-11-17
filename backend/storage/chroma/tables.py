"""Chroma catalog rows."""

from sqlalchemy import Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.base import Base

__all__ = [
    "ChromaRow",
]


class ChromaRow(Base):  # pylint: disable=too-few-public-methods
    """Chroma Row.
    """
    __tablename__ = "chroma"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    cyan: Mapped[int] = mapped_column(Integer)
    magenta: Mapped[int] = mapped_column(Integer)
    yellow: Mapped[int] = mapped_column(Integer)
    black: Mapped[int] = mapped_column(Integer)