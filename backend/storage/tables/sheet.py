from decimal import Decimal

from sqlalchemy import BigInteger, Identity, Integer, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.storage.tables.workplace_order import Base


class SheetRow(Base):
    __tablename__ = "sheet"
    __table_args__ = (
        UniqueConstraint("height", "width", "density", "cost"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    height: Mapped[int] = mapped_column(BigInteger, nullable=False)
    width: Mapped[int] = mapped_column(BigInteger, nullable=False)
    density: Mapped[int] = mapped_column(BigInteger, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
