from dataclasses import dataclass
from typing import Type

from src.storage.declarative_base import DeclarativeBase


@dataclass
class RepositoryConfig:
    name: str
    entity: Type[DeclarativeBase]
