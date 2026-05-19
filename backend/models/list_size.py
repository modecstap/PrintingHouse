from pydantic import BaseModel, Field


class ListSize(BaseModel):
    height: int = Field(
        description="Высота изделия в мм.",
        ge=0,
    )
    width: int = Field(
        description="Ширина изделия в мм.",
        ge=0,
    )
    bleeds: int
