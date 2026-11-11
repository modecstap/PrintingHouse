"""JSON request and response models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FormatDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    height: int
    width: int


class PaperDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    density: int
    thickness: Decimal
    name: str
    price_per_kilo: str

    @field_validator("thickness")
    @classmethod
    def validate_thickness(cls, value: Decimal) -> Decimal:
        if value <= 0:
            msg = f"толщина бумаги меньше или равна 0, толщина={value} мм"
            raise ValueError(msg)
        if value != value.quantize(Decimal("0.01")):
            msg = (
                f"толщина бумаги имеет более 2 знаков после запятой, "
                f"толщина={value} мм"
            )
            raise ValueError(msg)
        return value


class SheetDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    paper: PaperDto
    format: FormatDto


class ImpositionDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    target: FormatDto
    sheet_id: int
    bleeds: int
    spacing: int


class PrintOpDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    kind: Literal["print"]
    printer_id: int
    operator_id: int
    chroma: Literal[
        "ZERO_ZERO",
        "ONE_ZERO",
        "ONE_ONE",
        "FOUR_ZERO",
        "FOUR_ONE",
        "FOUR_FOUR",
    ]


class FilmDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    price: str
    density: int


class FilmReadDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    price: str
    density: int


class SheetReadDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    paper: PaperDto
    format: FormatDto


class CreatedIdDto(BaseModel):
    id: int


class LaminateOpDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    kind: Literal["laminate"]
    laminator_id: int
    operator_id: int
    lamination: Literal["DONT", "ONE_ZERO", "ONE_ONE"]
    film_id: int


class CutOpDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    kind: Literal["cut"]
    cutter_id: int
    operator_id: int


class DieCutOpDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    kind: Literal["die_cut"]
    operator_id: int


RunOperationDto = Annotated[
    PrintOpDto | LaminateOpDto | CutOpDto | DieCutOpDto,
    Field(discriminator="kind"),
]


class PartDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    imposition: ImpositionDto
    count: int
    markup: int
    operations: tuple[RunOperationDto, ...]


class AdditionalWorkDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    price: str
    description: str
    markup: int


class ProductDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    blocks: tuple[PartDto, ...]
    operations: tuple[AdditionalWorkDto, ...] = ()


class OrderWriteDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    product: ProductDto
    count: int
    description: str = ""


class OrderDto(BaseModel):
    id: int
    count: int
    description: str
    created_at: datetime
    product: ProductDto


class OrderReportDto(BaseModel):
    product_price: str
    order_price: str
    income: str
    impositions: tuple[int, ...]


class SaveOrderResponseDto(BaseModel):
    id: int


class ReferenceDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    description: str
    order_id: int


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class PrinterDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    startup: str
    cyan: str
    magenta: str
    yellow: str
    black: str


class LaminatorDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    startup: str


class CutterDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    max_stack: int


class OperatorDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    salary_by_operation: str
