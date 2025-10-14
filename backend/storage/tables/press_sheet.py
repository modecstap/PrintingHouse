from sqlalchemy import Column, BigInteger, Sequence, text, Integer
from sqlalchemy.orm import relationship

from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class PressSheetEntity(Base):
    __tablename__ = 'press_sheet'

    # ПОЛЯ ТАБЛИЦЫ
    id = Column(
        BigInteger,
        Sequence('press_sheet_id_seq', start=1, increment=1),
        primary_key=True,
        server_default=text("nextval('press_sheet_id_seq')")
    )
    height = Column(Integer, nullable=False, comment="Высота в мм")
    width = Column(Integer, nullable=False, comment="Ширина в мм")
    spacing = Column(Integer, nullable=False, comment="Поля в мм")

    # ИСХОДЯЩИЕ ОТНОШЕНИЯ
    production = relationship('ProductionEntity', back_populates='press_sheet', lazy='selectin')

    # ВХОДЯЩИЕ ОТНОШЕНИЯ
