from pydantic import BaseModel, Field

from backend.models.chroma import Chroma
from backend.models.lamination import Lamination
from backend.models.list_size import ListSize


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
