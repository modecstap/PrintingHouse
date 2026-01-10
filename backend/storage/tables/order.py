from sqlalchemy import Column, BigInteger, Date, text, Sequence, ForeignKey, Enum, String
from sqlalchemy.orm import relationship

from backend.models.status import Status
from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class OrderEntity(Base):
    __tablename__ = 'order'

    # ПОЛЯ ТАБЛИЦЫ

    id = Column(
        BigInteger,
        Sequence('order_id_seq', start=1, increment=1),
        primary_key=True,
        server_default=text("nextval('order_id_seq')")
    )
    order_cost_report_id = Column(ForeignKey('order_cost_report.id', onupdate="CASCADE", ondelete="CASCADE"))
    economy_id = Column(ForeignKey('economy.id', onupdate="CASCADE", ondelete="CASCADE"))

    creation_date = Column(Date, nullable=False)
    status = Column(Enum(Status, name="order_status"), nullable=False)
    comment = Column(String(500), nullable=False)
    unit_count = Column(BigInteger, nullable=True)

    # ИСХОДЯЩИЕ ОТНОШЕНИЯ

    cost_report = relationship('OrderCostReportEntity', back_populates='order', lazy='selectin')
    economy = relationship('EconomyEntity', back_populates='order', lazy='selectin')

    # ВХОДЯЩИЕ ОТНОШЕНИЯ

    operations = relationship('OperationEntity', back_populates='order', lazy='selectin', uselist=True)
    printings = relationship('PrintingEntity', back_populates='order', lazy='selectin', uselist=True)
