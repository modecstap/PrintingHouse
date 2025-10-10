from sqlalchemy.orm import declarative_base

from backend.storage.singleton import Singleton


class DeclarativeBase(metaclass=Singleton):
    _base = None

    def __init__(self):
        if DeclarativeBase._base is None:
            DeclarativeBase._base = declarative_base()

    @property
    def base(self):
        return DeclarativeBase._base
