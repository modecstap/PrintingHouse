from sqlalchemy import Column, BigInteger, Numeric, text, Sequence, Integer, ForeignKey
from sqlalchemy.orm import relationship

from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class PrintingCostReportEntity(Base):
    __tablename__ = 'printing_cost_report'

    # ПОЛЯ ТАБЛИЦЫ

    id = Column(
        BigInteger,
        Sequence('cost_report_id_seq', start=1, increment=1),
        primary_key=True,
        server_default=text("nextval('cost_report_id_seq')")
    )
    order_cost_report_id = Column(ForeignKey('order_cost_report.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    items_per_sheet = Column(Integer, nullable=False)
    sheet_count = Column(Integer, nullable=False)
    unit_cost_price = Column(Numeric, nullable=False)
    unit_cost = Column(Numeric, nullable=False)
    edition_cost = Column(Numeric, nullable=False)
    edition_cost_price = Column(Numeric, nullable=False)
    profit_before_tax = Column(Numeric, nullable=False)
    profit_after_tax = Column(Numeric, nullable=False)

    # ИСХОДЯЩИЕ ОТНОШЕНИЯ

    order_cost_report = relationship('OrderCostReportEntity', back_populates='printing_cost_reports', lazy='selectin')

    # ВХОДЯЩИЕ ОТНОШЕНИЯ

    printing = relationship('PrintingEntity', back_populates='cost_report', lazy='selectin')
