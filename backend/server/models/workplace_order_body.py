from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Annotated, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer

from backend.workplace.accountant.money import Money
from backend.workplace.accountant.pricing.cutting import CuttingCalculation
from backend.workplace.accountant.pricing.die_cutting import (
    DieCuttingCalculation,
)
from backend.workplace.accountant.pricing.lamination import (
    LaminationCalculation,
)
from backend.workplace.accountant.pricing.printing import PrintingCalculation
from backend.workplace.cost_order import List, Order, Printing, Status
from backend.workplace.reports import CostReport, PrintingCost
from backend.workplace.workplaces.lamination.models import Lamination
from backend.workplace.workplaces.printing.models import Chroma, PressSheet

_EnumT = TypeVar("_EnumT", bound=Enum)

_STATUS_BY_LABEL = {member.value: member for member in Status}


def _parse_decimal(value: object) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if type(value) is str:
        try:
            return Decimal(value)
        except InvalidOperation as error:
            raise ValueError("ожидается десятичная строка") from error
    raise ValueError("ожидается десятичная строка")


def _decimal_to_json(value: Decimal) -> str:
    return str(value)


def _parse_int(value: object) -> int:
    if type(value) is int:
        return value
    raise ValueError("ожидается целое число")


def _parse_bool(value: object) -> bool:
    if type(value) is bool:
        return value
    raise ValueError("ожидается булево значение")


def _parse_optional_id(value: object) -> int | None:
    if value is None or type(value) is int:
        return value
    raise ValueError("ожидается целое id или null")


def _parse_status(value: object) -> Status:
    if isinstance(value, Status):
        return value
    if type(value) is str and value in _STATUS_BY_LABEL:
        return _STATUS_BY_LABEL[value]
    raise ValueError("ожидается подпись статуса")


def _status_to_json(value: Status) -> str:
    return value.value


def _member_name(
    enum_type: type[_EnumT],
) -> Callable[[object], _EnumT]:
    def parse(value: object) -> _EnumT:
        if isinstance(value, enum_type):
            return value
        if type(value) is str and value in enum_type.__members__:
            return enum_type[value]
        raise ValueError("ожидается имя члена перечисления")

    return parse


def _enum_name_to_json(value: Enum) -> str:
    return value.name


JsonDecimal = Annotated[
    Decimal,
    BeforeValidator(_parse_decimal),
    PlainSerializer(
        _decimal_to_json, when_used="json", return_type=str
    ),
]
StrictInt = Annotated[int, BeforeValidator(_parse_int)]
StrictBool = Annotated[bool, BeforeValidator(_parse_bool)]
OptionalOrderId = Annotated[
    int | None, BeforeValidator(_parse_optional_id)
]
JsonStatus = Annotated[
    Status,
    BeforeValidator(_parse_status),
    PlainSerializer(_status_to_json, when_used="json", return_type=str),
]
JsonChroma = Annotated[
    Chroma,
    BeforeValidator(_member_name(Chroma)),
    PlainSerializer(
        _enum_name_to_json, when_used="json", return_type=str
    ),
]
JsonLamination = Annotated[
    Lamination,
    BeforeValidator(_member_name(Lamination)),
    PlainSerializer(
        _enum_name_to_json, when_used="json", return_type=str
    ),
]


class WorkplaceListBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    width: StrictInt
    height: StrictInt
    bleeds: StrictInt


class WorkplacePressSheetBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    density: StrictInt
    width: StrictInt
    height: StrictInt
    spacing: StrictInt


class WorkplacePressPricingBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    cyan: JsonDecimal
    magenta: JsonDecimal
    yellow: JsonDecimal
    black: JsonDecimal
    paper: JsonDecimal
    salary: JsonDecimal


class WorkplaceCutPricingBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    salary: JsonDecimal


class WorkplaceLaminationPricingBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    startup: JsonDecimal
    film_cost: JsonDecimal
    salary: JsonDecimal


class WorkplaceDieCutPricingBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    salary: JsonDecimal


class WorkplacePrintingBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    count: StrictInt
    chroma: JsonChroma
    lamination: JsonLamination
    die_cutting: StrictBool
    sheet_by_fitting: StrictInt
    stack_height: StrictInt
    press_sheet: WorkplacePressSheetBody
    list: WorkplaceListBody
    press_pricing: WorkplacePressPricingBody
    cut_pricing: WorkplaceCutPricingBody
    lamination_pricing: WorkplaceLaminationPricingBody
    die_cut_pricing: WorkplaceDieCutPricingBody


class WorkplaceOrderBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    unit_count: StrictInt
    tax_rate: JsonDecimal
    markup: JsonDecimal
    operation_costs: list[JsonDecimal]
    printings: list[WorkplacePrintingBody]
    id: OptionalOrderId = None
    comment: str = ""
    status: JsonStatus = Status.SAVED


class WorkplacePrintingCostBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    items_per_sheet: StrictInt
    sheet_count: StrictInt
    unit_cost_price: JsonDecimal
    unit_cost: JsonDecimal
    edition_cost_price: JsonDecimal
    edition_cost: JsonDecimal
    profit_before_tax: JsonDecimal
    profit_after_tax: JsonDecimal


class WorkplaceCostReportBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    unit_cost_price: JsonDecimal
    unit_cost: JsonDecimal
    edition_cost: JsonDecimal
    profit_after_tax: JsonDecimal
    printing_cost_reports: list[WorkplacePrintingCostBody]


class WorkplaceSavedOrderBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: StrictInt


class WorkplaceAcceptedOrderBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: StrictInt
    cost_report: WorkplaceCostReportBody


class WorkplaceStatusChangeBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    order_id: StrictInt
    new_status: JsonStatus


def order_from_body(body: WorkplaceOrderBody) -> Order:
    """Собирает заказ рабочего места из принятого тела.

    Результат: Order с теми же данными расчёта, id, comment и status.
    operation_costs остаётся кортежем Decimal. Каждая ставка — Money
    от Decimal этого поля.
    Ошибки: InvalidPriceException, если ставка меньше нуля.
    """
    return Order(
        unit_count=body.unit_count,
        tax_rate=body.tax_rate,
        markup=body.markup,
        operation_costs=tuple(body.operation_costs),
        printings=tuple(
            _printing_from_body(item) for item in body.printings
        ),
        id=body.id,
        comment=body.comment,
        status=body.status,
    )


def body_from_order(order: Order) -> WorkplaceOrderBody:
    """Собирает тело заказа из заказа рабочего места.

    Результат: те же поля. Порядок operation_costs и printings
    сохраняется. Ставка в поле — amount, не объект Money.
    """
    return WorkplaceOrderBody(
        unit_count=order.unit_count,
        tax_rate=order.tax_rate,
        markup=order.markup,
        operation_costs=list(order.operation_costs),
        printings=[
            _body_from_printing(item) for item in order.printings
        ],
        id=order.id,
        comment=order.comment,
        status=order.status,
    )


def body_from_report(report: CostReport) -> WorkplaceCostReportBody:
    """Собирает тело отчёта из CostReport.

    Результат: те же суммы. Порядок printing_cost_reports сохраняется.
    """
    return WorkplaceCostReportBody(
        unit_cost_price=report.unit_cost_price,
        unit_cost=report.unit_cost,
        edition_cost=report.edition_cost,
        profit_after_tax=report.profit_after_tax,
        printing_cost_reports=[
            _body_from_printing_cost(item)
            for item in report.printing_cost_reports
        ],
    )


def _printing_from_body(body: WorkplacePrintingBody) -> Printing:
    press = body.press_pricing
    sheet = body.press_sheet
    page = body.list
    lamination = body.lamination_pricing
    return Printing(
        count=body.count,
        chroma=body.chroma,
        lamination=body.lamination,
        die_cutting=body.die_cutting,
        sheet_by_fitting=body.sheet_by_fitting,
        stack_height=body.stack_height,
        press_sheet=PressSheet(
            density=sheet.density,
            width=sheet.width,
            height=sheet.height,
            spacing=sheet.spacing,
        ),
        list=List(
            width=page.width,
            height=page.height,
            bleeds=page.bleeds,
        ),
        press_pricing=PrintingCalculation(
            Money(press.cyan),
            Money(press.magenta),
            Money(press.yellow),
            Money(press.black),
            Money(press.paper),
            Money(press.salary),
        ),
        cut_pricing=CuttingCalculation(Money(body.cut_pricing.salary)),
        lamination_pricing=LaminationCalculation(
            Money(lamination.startup),
            Money(lamination.film_cost),
            Money(lamination.salary),
        ),
        die_cut_pricing=DieCuttingCalculation(
            Money(body.die_cut_pricing.salary)
        ),
    )


def _body_from_printing(printing: Printing) -> WorkplacePrintingBody:
    press = printing.press_pricing
    sheet = printing.press_sheet
    page = printing.list
    lamination = printing.lamination_pricing
    return WorkplacePrintingBody(
        count=printing.count,
        chroma=printing.chroma,
        lamination=printing.lamination,
        die_cutting=printing.die_cutting,
        sheet_by_fitting=printing.sheet_by_fitting,
        stack_height=printing.stack_height,
        press_sheet=WorkplacePressSheetBody(
            density=sheet.density,
            width=sheet.width,
            height=sheet.height,
            spacing=sheet.spacing,
        ),
        list=WorkplaceListBody(
            width=page.width,
            height=page.height,
            bleeds=page.bleeds,
        ),
        press_pricing=WorkplacePressPricingBody(
            cyan=press.cyan.amount,
            magenta=press.magenta.amount,
            yellow=press.yellow.amount,
            black=press.black.amount,
            paper=press.paper.amount,
            salary=press.salary.amount,
        ),
        cut_pricing=WorkplaceCutPricingBody(
            salary=printing.cut_pricing.salary.amount
        ),
        lamination_pricing=WorkplaceLaminationPricingBody(
            startup=lamination.startup.amount,
            film_cost=lamination.film_cost.amount,
            salary=lamination.salary.amount,
        ),
        die_cut_pricing=WorkplaceDieCutPricingBody(
            salary=printing.die_cut_pricing.salary.amount
        ),
    )


def _body_from_printing_cost(
    item: PrintingCost,
) -> WorkplacePrintingCostBody:
    return WorkplacePrintingCostBody(
        items_per_sheet=item.items_per_sheet,
        sheet_count=item.sheet_count,
        unit_cost_price=item.unit_cost_price,
        unit_cost=item.unit_cost,
        edition_cost_price=item.edition_cost_price,
        edition_cost=item.edition_cost,
        profit_before_tax=item.profit_before_tax,
        profit_after_tax=item.profit_after_tax,
    )
