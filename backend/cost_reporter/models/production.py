from decimal import Decimal

from pydantic import BaseModel, Field

from backend.cost_reporter.models.press_sheet import PressSheet


class CutterInfo(BaseModel):
    stack_height: int = Field(description="Высота стопки помещающейся в резаке в мм")


class Production(BaseModel):
    tax_rate: Decimal = Field(description="Налоговая ставка (0,93 = 7%)")
    black_ink_cost: Decimal = Field(description="Стоимость чёрной краски на 1 листе в руб.")
    ink_cost: Decimal = Field(description="Стоимость всех красок на 1 листе в руб.")
    printer_salary: Decimal = Field(description="Зарплата печатнику за 1 лист в руб.ы")
    lamination_cost: Decimal = Field(description="Цена ламинации 1 листа в руб.")
    die_cutting_cost: Decimal = Field(description="Стоимость высечки 1 листа в руб.")
    paper_cost: Decimal = Field(description="Стоимость 1кг бумаги в руб.")
    press_sheet: PressSheet
    cutter: CutterInfo
    cutting_cost: Decimal = Field(description="Цена 1 реза в руб.")
    sheet_by_fitting: int = Field(description="Количество листов на приладку в шт.")
    markup: Decimal = Field(
        description="Наценка в %",
        gt=Decimal("0"),
    )
