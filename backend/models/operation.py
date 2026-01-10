from decimal import Decimal

from pydantic import BaseModel, Field


class Operation(BaseModel):
    name: str = Field(description="Название операции.")
    cost: Decimal = Field(gt=0, description="Стоимость операции.")
    description: str = Field(description="Описание операции.")
