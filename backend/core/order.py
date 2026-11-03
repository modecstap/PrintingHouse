from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from backend.core.accountant.money import Money
from backend.core.accountant.pricing.cutting import CuttingCalculation
from backend.core.accountant.pricing.die_cutting import \
    DieCuttingCalculation
from backend.core.accountant.pricing.lamination import \
    LaminationCalculation
from backend.core.accountant.pricing.printing import \
    PrintingCalculation
from backend.core.workplaces.lamination.models import Lamination
from backend.core.workplaces.printing.models import Chroma


@dataclass(frozen=True)
class List:
    width: int
    height: int
    bleeds: int


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
class OrderSpecification:
    unit_count: int
    markup: Decimal
    operations: tuple[Operation, ...]


@dataclass(frozen=True)
class PrintingSpecification:
    count: int
    chroma: Chroma
    lamination: Lamination
    die_cutting: bool
    spacing: int
    press_sheet: int | None
    list: List
    sheet_by_fitting: int


@dataclass(frozen=True)
class StoredPress:
    """Size and paper rate copied from the sheet row when an order is read.

    The printing row stores the sheet id. These four numbers stay on the
    printing until the order service loads the sheet catalog.
    """

    density: int
    width: int
    height: int
    paper: Money


@dataclass(frozen=True)
class Printing:
    specification: PrintingSpecification
    stack_height: int
    press_pricing: PrintingCalculation
    cut_pricing: CuttingCalculation
    lamination_pricing: LaminationCalculation
    die_cut_pricing: DieCuttingCalculation
    stored_press: StoredPress
    comment: str = ""


@dataclass(frozen=True)
class Order:
    specification: OrderSpecification
    tax_rate: Decimal
    printings: tuple[Printing, ...]
    id: int | None = None
    comment: str = ""
    status: Status = Status.SAVED
    creation_date: date | None = None


def empty_reference_order() -> Order:
    """Returns the order of an empty reference.

    :return: unit_count is 1, tax and markup are zero, there are no operations,
    and one printing has zero numbers and zero rates. press_sheet and spacing
    are empty. The status is Отложен. id and creation_date are empty.
    This function does not insert a sheet row.
    """
    zero = Decimal("0")
    rate = Money(zero)
    printing = Printing(
        specification=PrintingSpecification(
            count=0,
            chroma=Chroma.ZERO_ZERO,
            lamination=Lamination.DONT,
            die_cutting=False,
            spacing=0,
            press_sheet=None,
            list=List(0, 0, 0),
            sheet_by_fitting=0,
        ),
        stack_height=0,
        press_pricing=PrintingCalculation(rate, rate, rate, rate, rate),
        cut_pricing=CuttingCalculation(rate),
        lamination_pricing=LaminationCalculation(rate, rate, rate),
        die_cut_pricing=DieCuttingCalculation(rate),
        stored_press=StoredPress(0, 0, 0, rate),
        comment="",
    )
    return Order(
        specification=OrderSpecification(
            unit_count=1,
            markup=zero,
            operations=(),
        ),
        tax_rate=zero,
        printings=(printing,),
        id=None,
        comment="",
        status=Status.SAVED,
        creation_date=None,
    )
