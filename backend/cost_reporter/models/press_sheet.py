from pydantic import BaseModel, Field


class PressSheet(BaseModel):
    height: int = Field(description="Высота в мм")
    width: int = Field(description="Ширина в мм")
    spacing: int = Field(description="Поля в мм")
