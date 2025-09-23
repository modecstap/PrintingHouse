from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field

from backend.cost_reporter.models.list_size import ListSize


class Chroma(Enum):
    ONE_ZERO = 1
    ONE_ONE = 2
    FOUR_ZERO = 3
    FOUR_ONE = 4
    FOUR_FOUR = 5


class Lamination(Enum):
    DONT = 1
    ONE_ZERO = 2
    ONE_ONE = 3


class Edition(BaseModel):
    count: int = Field(
        description="Кол-во изделий шт.",
        gt=0,
        le=1_000_000,
    )
    list_size: ListSize = Field(description="Формат листа")
    density: int = Field(
        description="Плотность бумаги в гр./м^2",
        ge=65,
    )
    chroma: Chroma = Field(description="Цветность бумаги")
    lamination: Lamination = Field(description="Ламинация")
    die_cutting: bool = Field(description="Наличие высечки")
    markup: Decimal = Field(
        description="Наценка (1.85 - наценка в 85%)",
        gt=Decimal("0"),
    )
