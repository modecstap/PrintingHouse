from sqlalchemy import BigInteger, Sequence, text, Integer, Column
from sqlalchemy.orm import relationship

from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class CutterInfoEntity(Base):
    __tablename__ = 'cutter_info'

    # ПОЛЯ ТАБЛИЦЫ
    id = Column(
        BigInteger,
        Sequence('cutter_info_id_seq', start=1, increment=1),
        primary_key=True,
        server_default=text("nextval('cutter_info_id_seq')")
    )
    stack_height = Column(Integer, nullable=False, comment="Высота стопки помещающейся в резаке в мм")

    # ИСХОДЯЩИЕ ОТНОШЕНИЯ

    # ВХОДЯЩИЕ ОТНОШЕНИЯ
    production = relationship('ProductionEntity', back_populates='cutter', lazy='selectin')
