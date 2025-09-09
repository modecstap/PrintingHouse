from decimal import Decimal

from pydantic import BaseModel, Field

from models.press_sheet import PressSheet


class CutterInfo:
    pass


class Production(BaseModel):
    tax_rate: Decimal = Field(description="Налоговая ставка (0,93 = 7%)")
    ink_cost: Decimal = Field(description="Стоимость красок на 1 листе в руб.")
    paper_cost: Decimal = Field(description="Стоимость 1кг бумаги в руб.")
    press_sheet: PressSheet
    cutter: CutterInfo
    cutting_cost: Decimal = Field(description="Цена 1 реза в руб.")
