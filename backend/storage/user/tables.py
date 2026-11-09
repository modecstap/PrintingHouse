"""Application users for JWT login."""

from sqlalchemy import Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.schema import Base


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
