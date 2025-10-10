from sqlalchemy import Column, BigInteger, text, Sequence, Integer, ForeignKey, Enum, BOOLEAN
from sqlalchemy.orm import relationship

from backend.models import Chroma, Lamination
from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class EditionEntity(Base):
    __tablename__ = 'edition'

    # ПОЛЯ ТАБЛИЦЫ

    id = Column(
        BigInteger,
        Sequence('edition_id_seq', start=1, increment=1),
        primary_key=True,
        server_default=text("nextval('edition_id_seq')")
    )
    list_size_id = Column(ForeignKey('list_size.id', onupdate="CASCADE", ondelete="CASCADE"))
    count = Column(Integer, nullable=False)
    density = Column(Integer, nullable=False)
    chroma = Column(Enum(Chroma, name="chroma"), nullable=False)
    lamination = Column(Enum(Lamination, name="lamination"), nullable=False)
    die_cutting = Column(BOOLEAN, nullable=False)

    # ИСХОДЯЩИЕ ОТНОШЕНИЯ

    list_size = relationship('ListSizeEntity', back_populates='edition', lazy='selectin')

    # ВХОДЯЩИЕ ОТНОШЕНИЯ

    order = relationship('OrderEntity', back_populates='edition', lazy='selectin')
