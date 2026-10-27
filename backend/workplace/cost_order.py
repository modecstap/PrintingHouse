from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from backend.workplace.accountant.money import Money
from backend.workplace.accountant.pricing.cutting import CuttingCalculation
from backend.workplace.accountant.pricing.die_cutting import \
    DieCuttingCalculation
from backend.workplace.accountant.pricing.lamination import \
    LaminationCalculation
from backend.workplace.accountant.pricing.printing import \
    PrintingCalculation
from backend.workplace.workplaces.lamination.models import Lamination
from backend.workplace.workplaces.printing.models import PressSheet, Chroma


@dataclass(frozen=True)
class List:
    width: int
    height: int
    bleeds: int

@dataclass(frozen=True)
class Printing:
    count: int
    chroma: Chroma
    lamination: Lamination
    die_cutting: bool
    sheet_by_fitting: int
    stack_height: int
    press_sheet: PressSheet
    list: List
    press_pricing: PrintingCalculation
    cut_pricing: CuttingCalculation
    lamination_pricing: LaminationCalculation
    die_cut_pricing: DieCuttingCalculation
    comment: str = ""


class Status(Enum):
    SAVED = "Отложен"
    IN_WORK = "В работе"
    DONE = "Завершён"


@dataclass(frozen=True)
class Operation:
    name: str
    cost: Decimal
    description: str


@dataclass(frozen=True)
class Order:
    unit_count: int
    tax_rate: Decimal
    markup: Decimal
    operations: tuple[Operation, ...]
    printings: tuple[Printing, ...]
    id: int | None = None
    comment: str = ""
    status: Status = Status.SAVED
    creation_date: date | None = None


def empty_reference_order() -> Order:
    """Возвращает заказ пустого справочника.

    Результат: unit_count 1, налог и наценка ноль, операций нет,
    одна печать с нулевыми числами и ставками, статус «Отложен».
    id и creation_date пустые.
    Побочные эффекты: базу не читает и не пишет.
    """
    zero = Decimal("0")
    rate = Money(zero)
    printing = Printing(
        count=0,
        chroma=Chroma.ZERO_ZERO,
        lamination=Lamination.DONT,
        die_cutting=False,
        sheet_by_fitting=0,
        stack_height=0,
        press_sheet=PressSheet(0, 0, 0, 0),
        list=List(0, 0, 0),
        press_pricing=PrintingCalculation(
            rate, rate, rate, rate, rate, rate
        ),
        cut_pricing=CuttingCalculation(rate),
        lamination_pricing=LaminationCalculation(rate, rate, rate),
        die_cut_pricing=DieCuttingCalculation(rate),
        comment="",
    )
    return Order(
        unit_count=1,
        tax_rate=zero,
        markup=zero,
        operations=(),
        printings=(printing,),
        id=None,
        comment="",
        status=Status.SAVED,
        creation_date=None,
    )
