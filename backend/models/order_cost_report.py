from decimal import Decimal

from pydantic import BaseModel, Field


class OrderCostReport(BaseModel):
    unit_cost_price: Decimal = Field(description="Себестоимость изделия руб.")
    unit_cost: Decimal = Field(description="Цена изделия руб.")
    edition_cost: Decimal = Field(description="Цена тиража руб.")
    profit_after_tax: Decimal = Field(description="Прибыль после уплаты налогов руб.")
