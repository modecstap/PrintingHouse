from collections.abc import Callable
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Annotated, TypeVar

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    PlainSerializer,
    model_serializer,
)

from backend.core.accountant.money import Money
from backend.core.accountant.pricing.cutting import CuttingCalculation
from backend.core.accountant.pricing.die_cutting import (
    DieCuttingCalculation,
)
from backend.core.accountant.pricing.lamination import (
    LaminationCalculation,
)
from backend.core.accountant.pricing.printing import PrintingCalculation
from backend.core.order import (
    List,
    Operation,
    Order,
    OrderSpecification,
    Printing,
    PrintingSpecification,
    Status,
)
from backend.core.errors import InvalidPriceException
from backend.core.reports import CostReport, PrintingCost
from backend.core.workplaces.lamination.models import Lamination
from backend.core.workplaces.printing.models import Chroma

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
OptionalSheetId = Annotated[
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


class WorkplacePressPricingBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    cyan: JsonDecimal
    magenta: JsonDecimal
    yellow: JsonDecimal
    black: JsonDecimal
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
    stack_height: StrictInt
    spacing: StrictInt
    press_sheet: OptionalSheetId
    list: WorkplaceListBody
    press_pricing: WorkplacePressPricingBody
    cut_pricing: WorkplaceCutPricingBody
    lamination_pricing: WorkplaceLaminationPricingBody
    die_cut_pricing: WorkplaceDieCutPricingBody
    comment: str = ""


class WorkplaceOperationBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    cost: JsonDecimal
    description: str


class WorkplaceOrderBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    unit_count: StrictInt
    tax_rate: JsonDecimal
    markup: JsonDecimal
    operations: list[WorkplaceOperationBody]
    printings: list[WorkplacePrintingBody]
    id: OptionalOrderId = None
    comment: str = ""
    status: JsonStatus = Status.SAVED
    creation_date: date | None = None

    @model_serializer(mode="wrap", when_used="json")
    def _omit_empty_creation_date(
        self,
        handler: Callable[["WorkplaceOrderBody"], dict[str, object]],
    ) -> dict[str, object]:
        # Ключ creation_date убирается только когда даты нет.
        # id: null в этом же ответе остаётся.
        data = handler(self)
        if data.get("creation_date") is None:
            data.pop("creation_date")
        return data


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
    """Builds a workplace order from the accepted body.

    :param body:

    :raises InvalidPriceException: if a rate is below zero
    or an operation cost is below zero. Zero is allowed.

    :return: an Order with calculation data, id, comment, and status.
    creation_date of the result is always None: the insert sets the date.
    operations is a tuple of Operation.
    Each printing rate is a Money from the Decimal of that field.
    """
    for item in body.operations:
        if item.cost < 0:
            raise InvalidPriceException(
                "сборка заказа: операция "
                f"{item.name!r} стоит {item.cost}, меньше нуля"
            )
    return Order(
        specification=OrderSpecification(
            unit_count=body.unit_count,
            markup=body.markup,
            operations=tuple(
                Operation(item.name, item.cost, item.description)
                for item in body.operations
            ),
        ),
        tax_rate=body.tax_rate,
        printings=tuple(
            _printing_from_body(item) for item in body.printings
        ),
        id=body.id,
        comment=body.comment,
        status=body.status,
    )


def body_from_order(order: Order) -> WorkplaceOrderBody:
    """Builds an order body from a workplace order.

    :param order:

    :return: the same fields. The order of operations and printings is kept.
    An operation cost and a rate in a field are Decimal, not a Money object.
    creation_date is copied. An empty date is not included in the JSON.
    """
    spec = order.specification
    return WorkplaceOrderBody(
        unit_count=spec.unit_count,
        tax_rate=order.tax_rate,
        markup=spec.markup,
        operations=[
            WorkplaceOperationBody(
                name=item.name,
                cost=item.cost,
                description=item.description,
            )
            for item in spec.operations
        ],
        printings=[
            _body_from_printing(item) for item in order.printings
        ],
        id=order.id,
        comment=order.comment,
        status=order.status,
        creation_date=order.creation_date,
    )


def body_from_report(report: CostReport) -> WorkplaceCostReportBody:
    """Builds a report body from a CostReport.

    :param report:

    :return: the same sums. The order of printing_cost_reports is kept.
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
    page = body.list
    lamination = body.lamination_pricing
    # JSON несёт id листа. Размер и ставка живут в справочнике.
    # Нулевой StoredPress не пишется: чтение собирает его из строки sheet.
    return Printing(
        specification=PrintingSpecification(
            count=body.count,
            chroma=body.chroma,
            lamination=body.lamination,
            die_cutting=body.die_cutting,
            spacing=body.spacing,
            press_sheet=body.press_sheet,
            list=List(
                width=page.width,
                height=page.height,
                bleeds=page.bleeds,
            ),
        ),
        stack_height=body.stack_height,
        press_pricing=PrintingCalculation(
            Money(press.cyan),
            Money(press.magenta),
            Money(press.yellow),
            Money(press.black),
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
        comment=body.comment,
    )


def _body_from_printing(printing: Printing) -> WorkplacePrintingBody:
    press = printing.press_pricing
    spec = printing.specification
    page = spec.list
    lamination = printing.lamination_pricing
    return WorkplacePrintingBody(
        count=spec.count,
        chroma=spec.chroma,
        lamination=spec.lamination,
        die_cutting=spec.die_cutting,
        stack_height=printing.stack_height,
        spacing=spec.spacing,
        press_sheet=spec.press_sheet,
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
        comment=printing.comment,
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
