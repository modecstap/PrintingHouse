from sqlalchemy import Column, BigInteger, Identity, Numeric, ForeignKey, String
from sqlalchemy.orm import relationship

from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class OperationEntity(Base):
    __tablename__ = 'operation'

    # ПОЛЯ ТАБЛИЦЫ

    id = Column(
        BigInteger,
        Identity(start=1),
        primary_key=True,
    )
    order_id = Column(ForeignKey('order.id', onupdate="CASCADE", ondelete="CASCADE"))

    name = Column(String(500), nullable=False, comment="Название операции.")
    cost = Column(Numeric(10, 4), nullable=False, comment="Стоимость операции в руб.")
    description = Column(String(500), nullable=True, comment="Описание операции")


    # ИСХОДЯЩИЕ ОТНОШЕНИЯ

    order = relationship('OrderEntity', back_populates='operations', lazy='selectin')

    # ВХОДЯЩИЕ ОТНОШЕНИЯ



