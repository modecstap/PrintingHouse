from decimal import Decimal

from pydantic import BaseModel, Field


class Economy(BaseModel):
    tax_rate: Decimal = Field(description="Налоговая ставка (0,93 = 7%)")
    markup: Decimal = Field(gt=Decimal("0"), description="Наценка в %")
