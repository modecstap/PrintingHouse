from sqlalchemy import Column, BigInteger, Sequence, text, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship

from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class ProductionEntity(Base):
    __tablename__ = 'production'

    # ПОЛЯ ТАБЛИЦЫ
    id = Column(
        BigInteger,
        Sequence('production_id_seq', start=1, increment=1),
        primary_key=True,
        server_default=text("nextval('production_id_seq')")
    )
    press_sheet_id = Column(ForeignKey('press_sheet.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    cutter_id = Column(ForeignKey('cutter_info.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    black_ink_cost = Column(Numeric(10, 4), nullable=False, comment="Стоимость чёрной краски на 1 листе в руб.")
    ink_cost = Column(Numeric(10, 4), nullable=False, comment="Стоимость всех красок на 1 листе в руб.")
    printer_salary = Column(Numeric(10, 4), nullable=False, comment="Зарплата печатнику за 1 лист в руб.")
    lamination_cost = Column(Numeric(10, 4), nullable=False, comment="Цена ламинации 1 листа в руб.")
    die_cutting_cost = Column(Numeric(10, 4), nullable=False, comment="Стоимость высечки 1 листа в руб.")
    paper_cost = Column(Numeric(10, 4), nullable=False, comment="Стоимость 1кг бумаги в руб.")
    cutting_cost = Column(Numeric(10, 4), nullable=False, comment="Цена 1 реза в руб.")
    sheet_by_fitting = Column(Integer, nullable=False, comment="Количество листов на приладку в шт.")

    # ИСХОДЯЩИЕ ОТНОШЕНИЯ
    press_sheet = relationship('PressSheetEntity', back_populates='production', lazy='selectin')
    cutter = relationship('CutterInfoEntity', back_populates='production', lazy='selectin')

    # ВХОДЯЩИЕ ОТНОШЕНИЯ
    printing = relationship('PrintingEntity', back_populates='production', lazy='selectin')
    reference = relationship('ProductionReferenceEntity', back_populates='production', lazy='selectin')
