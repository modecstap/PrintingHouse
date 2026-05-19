from pydantic import BaseModel, Field, model_validator

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

    @model_validator(mode="after")
    def validate_list_size(self):
        if self.die_cutting:
            min_size = 5
        else:
            min_size = 40

        if self.list_size.height < min_size or self.list_size.width < min_size:
            raise ValueError(f"Сторона листа должна быть не менее: {min_size}")

        return self
