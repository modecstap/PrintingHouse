from sqlalchemy import Column, BigInteger, Sequence, String, Boolean, DateTime, text, Enum
from sqlalchemy.sql import func

from backend.models.permission import Permission
from backend.storage.declarative_base import DeclarativeBase

Base = DeclarativeBase().base


class UserEntity(Base):
    __tablename__ = 'user'

    id = Column(
        BigInteger,
        Sequence('user_id_seq', start=1, increment=1),
        primary_key=True,
        server_default=text("nextval('user_id_seq')")
    )

    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text('true'))
    permissions = Column(Enum(Permission), nullable=False, server_default=Permission.NONE.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
