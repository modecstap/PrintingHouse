from sqlalchemy import Column, BigInteger, Sequence, text, Numeric, Integer, ForeignKey, String, Identity
from sqlalchemy.orm import relationship

from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class ProductionReferenceEntity(Base):
    __tablename__ = 'production_reference'

    # ПОЛЯ ТАБЛИЦЫ
    id = Column(
        BigInteger,
        Identity(start=1),
        primary_key=True,
    )
    production_id = Column(ForeignKey('production.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    comment = Column(String(500), nullable=True)

    # ИСХОДЯЩИЕ ОТНОШЕНИЯ
    production = relationship('ProductionEntity', back_populates='reference', lazy='selectin')
