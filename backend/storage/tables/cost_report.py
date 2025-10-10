from sqlalchemy import Column, BigInteger, Numeric, text, Sequence, Integer
from sqlalchemy.orm import relationship

from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class CostReportEntity(Base):
    __tablename__ = 'cost_report'

    # ПОЛЯ ТАБЛИЦЫ

    id = Column(
        BigInteger,
        Sequence('cost_report_id_seq', start=1, increment=1),
        primary_key=True,
        server_default=text("nextval('cost_report_id_seq')")
    )
    items_per_sheet = Column(Integer, nullable=False)
    sheet_count = Column(Integer, nullable=False)
    unit_cost_price = Column(Numeric, nullable=False)
    unit_cost = Column(Numeric, nullable=False)
    edition_cost = Column(Numeric, nullable=False)
    profit_before_tax = Column(Numeric, nullable=False)
    profit_after_tax = Column(Numeric, nullable=False)

    # ИСХОДЯЩИЕ ОТНОШЕНИЯ

    # ВХОДЯЩИЕ ОТНОШЕНИЯ

    order = relationship('OrderEntity', back_populates='cost_report', lazy='selectin')
