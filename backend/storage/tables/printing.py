from sqlalchemy import Column, BigInteger, Date, text, Sequence, ForeignKey, Enum, String
from sqlalchemy.orm import relationship

from backend.models.status import Status
from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class PrintingEntity(Base):
    __tablename__ = 'printing'

    # ПОЛЯ ТАБЛИЦЫ

    id = Column(
        BigInteger,
        Sequence('order_id_seq', start=1, increment=1),
        primary_key=True,
        server_default=text("nextval('order_id_seq')")
    )
    order_id = Column(ForeignKey('order.id', onupdate="CASCADE", ondelete="CASCADE"))
    production_id = Column(ForeignKey('production.id', onupdate="CASCADE", ondelete="CASCADE"))
    edition_id = Column(ForeignKey('edition.id', onupdate="CASCADE", ondelete="CASCADE"))
    printing_cost_report_id = Column(ForeignKey('printing_cost_report.id', onupdate="CASCADE", ondelete="CASCADE"))
    comment = Column(String(500), nullable=False)

    # ИСХОДЯЩИЕ ОТНОШЕНИЯ

    production = relationship('ProductionEntity', back_populates='printing', lazy='selectin')
    edition = relationship('EditionEntity', back_populates='printing', lazy='selectin')
    cost_report = relationship('PrintingCostReportEntity', back_populates='printing', lazy='selectin')
    order = relationship('OrderEntity', back_populates='printings', lazy='selectin')

    # ВХОДЯЩИЕ ОТНОШЕНИЯ
