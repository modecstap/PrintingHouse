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
    cost_report_id = Column(ForeignKey('cost_report.id', onupdate="CASCADE", ondelete="CASCADE"))
    edition_id = Column(ForeignKey('edition.id', onupdate="CASCADE", ondelete="CASCADE"))
    production_id = Column(ForeignKey('production.id', onupdate="CASCADE", ondelete="CASCADE"))

    creation_date = Column(Date, nullable=False)
    status = Column(Enum(Status, name="order_status"), nullable=False)
    comment = Column(String(500), nullable=False)

    # ИСХОДЯЩИЕ ОТНОШЕНИЯ

    production = relationship('ProductionEntity', back_populates='order', lazy='selectin')
    cost_report = relationship('CostReportEntity', back_populates='order', lazy='selectin')
    edition = relationship('EditionEntity', back_populates='order', lazy='selectin')

    # ВХОДЯЩИЕ ОТНОШЕНИЯ
