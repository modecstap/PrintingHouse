"""Named references to exemplar orders."""

from sqlalchemy import ForeignKey, Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.schema import Base


class OrderReferenceRow(Base):
    __tablename__ = "order_references"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))

