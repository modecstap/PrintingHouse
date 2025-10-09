from pydantic import BaseModel, Field


class ListSize(BaseModel):
    height: int = Field(
        description="Высота изделия в мм.",
        ge=40,
    )
    width: int = Field(
        description="Ширина изделия в мм.",
        ge=40,
    )
    bleeds: int
