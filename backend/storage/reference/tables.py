"""Named references to exemplar orders."""

from sqlalchemy import ForeignKey, Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.base import Base


__all__ = ["OrderReferenceRow"]

class OrderReferenceRow(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "order_references"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
