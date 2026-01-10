from sqlalchemy import Column, BigInteger, Identity, Numeric
from sqlalchemy.orm import relationship

from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class EconomyEntity(Base):
    __tablename__ = 'economy'

    # ПОЛЯ ТАБЛИЦЫ

    id = Column(
        BigInteger,
        Identity(start=1),
        primary_key=True,
    )
    markup = Column(Numeric(10, 4), nullable=False, comment="Наценка в %")
    tax_rate = Column(Numeric(10, 4), nullable=False, comment="Налоговая ставка (0,93 = 7%)")


    # ИСХОДЯЩИЕ ОТНОШЕНИЯ



    # ВХОДЯЩИЕ ОТНОШЕНИЯ

    order = relationship('OrderEntity', back_populates='economy', lazy='selectin')

