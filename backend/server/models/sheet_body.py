from decimal import Decimal, InvalidOperation
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    PlainSerializer,
)

from backend.core.accountant.money import Money
from backend.core.sheet.service import SaveSheet
from backend.core.sheet.sheet import Sheet


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


def _parse_optional_id(value: object) -> int | None:
    if value is None or type(value) is int:
        return value
    raise ValueError("ожидается целое id или null")


JsonDecimal = Annotated[
    Decimal,
    BeforeValidator(_parse_decimal),
    PlainSerializer(
        _decimal_to_json, when_used="json", return_type=str
    ),
]
StrictInt = Annotated[int, BeforeValidator(_parse_int)]
OptionalSheetId = Annotated[
    int | None, BeforeValidator(_parse_optional_id)
]


class SheetBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: OptionalSheetId = None
    name: str = ""
    height: StrictInt
    width: StrictInt
    density: StrictInt
    cost: JsonDecimal


class SheetSavedBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: StrictInt


def command_from_body(body: SheetBody) -> SaveSheet:
    """Builds a save command from the accepted body.

    :param body: name is accepted and is not part of the command.

    :raises InvalidPriceException: if cost is below zero. Zero is allowed.
    The catalog is unchanged.

    :return: the command. An empty id asks for an insert.
    """
    return SaveSheet(
        id=body.id,
        height=body.height,
        width=body.width,
        density=body.density,
        cost=Money(body.cost),
    )


def body_from_sheet(sheet: Sheet) -> SheetBody:
    """Builds a sheet body from a stored sheet.

    :param sheet:

    :return: id, name, height, width, density, and cost.
    version is not included. cost is the rate as Decimal.
    """
    return SheetBody(
        id=sheet.id,
        name=sheet.format.name,
        height=sheet.format.height,
        width=sheet.format.width,
        density=sheet.density,
        cost=sheet.cost.amount,
    )
