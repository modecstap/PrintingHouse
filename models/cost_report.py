from decimal import Decimal

from pydantic import BaseModel, Field


class CostReport(BaseModel):
    items_per_sheet: int = Field(description="Кол-во изделий на листе шт.")
    sheet_count: int = Field(description="Кол-во печатных листов шт.")
    unit_cost_price: Decimal = Field(description="Себестоимость изделия руб.")
    unit_cost: Decimal = Field(description="Цена изделия руб.")
    edition_cost: Decimal = Field(description="Цена тиража руб.")
    profit_before_tax: Decimal = Field(description="Прибыль до уплаты налогов руб.")
    profit_after_tax: Decimal = Field(description="Прибыль после уплаты налогов руб.")
