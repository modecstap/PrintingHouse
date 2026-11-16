"""SQLAlchemy declarative base for mapped persistence tables."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """SQLAlchemy metadata root for the new_core persistence schema."""
