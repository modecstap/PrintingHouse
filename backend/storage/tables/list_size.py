from sqlalchemy import Column, BigInteger, text, Sequence, Integer
from sqlalchemy.orm import relationship

from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class ListSizeEntity(Base):
    __tablename__ = 'list_size'

    # ПОЛЯ ТАБЛИЦЫ

    id = Column(
        BigInteger,
        Sequence('list_size_id_seq', start=1, increment=1),
        primary_key=True,
        server_default=text("nextval('list_size_id_seq')")
    )
    height = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    bleeds = Column(Integer, nullable=False)

    # ИСХОДЯЩИЕ ОТНОШЕНИЯ

    # ВХОДЯЩИЕ ОТНОШЕНИЯ

    edition = relationship('EditionEntity', back_populates='list_size', lazy='selectin')
