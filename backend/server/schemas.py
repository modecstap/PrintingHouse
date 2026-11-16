"""JSON request and response models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


__all__ = [
    "FormatDto",
    "PaperDto",
    "SheetDto",
    "ImpositionDto",
    "PrintOpDto",
    "FilmDto",
    "FilmReadDto",
    "SheetReadDto",
    "CreatedIdDto",
    "LaminateOpDto",
    "CutOpDto",
    "DieCutOpDto",
    "PartDto",
    "AdditionalWorkDto",
    "ProductDto",
    "OrderWriteDto",
    "OrderDto",
    "OrderReportDto",
    "SaveOrderResponseDto",
    "ReferenceDto",
    "LoginRequest",
    "TokenResponse",
    "PrinterDto",
    "LaminatorDto",
    "CutterDto",
    "OperatorDto",
    "PrinterWriteDto",
    "LaminatorWriteDto",
    "CutterWriteDto",
    "OperatorWriteDto",
]

class FormatDto(BaseModel):
    """Format Dto.
    """
    model_config = ConfigDict(extra="ignore")

    name: str
    height: int
    width: int


class PaperDto(BaseModel):
    """Paper Dto.
    """
    model_config = ConfigDict(extra="ignore")

    density: int
    thickness: Decimal
    name: str
    price_per_kilo: str

    @field_validator("thickness")
    @classmethod
    def validate_thickness(cls, value: Decimal) -> Decimal:
        """Validates thickness.

        :param value: the value.

        :raises ValueError: when the operation fails.

        :return: the Decimal result.
        """
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
    """Sheet Dto.
    """
    model_config = ConfigDict(extra="ignore")

    paper: PaperDto
    format: FormatDto


class ImpositionDto(BaseModel):
    """Imposition Dto.
    """
    model_config = ConfigDict(extra="ignore")

    target: FormatDto
    press_sheet: SheetReadDto
    bleeds: int
    spacing: int


class PrintOpDto(BaseModel):
    """Print Op Dto.
    """
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
    """Film Dto.
    """
    model_config = ConfigDict(extra="ignore")

    name: str
    price: str
    density: int


class FilmReadDto(BaseModel):
    """Film Read Dto.
    """
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    price: str
    density: int


class SheetReadDto(BaseModel):
    """Sheet Read Dto.
    """
    model_config = ConfigDict(extra="ignore")

    id: int
    paper: PaperDto
    format: FormatDto


class CreatedIdDto(BaseModel):
    """Created Id Dto.
    """
    id: int


class LaminateOpDto(BaseModel):
    """Laminate Op Dto.
    """
    model_config = ConfigDict(extra="ignore")

    kind: Literal["laminate"]
    laminator_id: int
    operator_id: int
    lamination: Literal["DONT", "ONE_ZERO", "ONE_ONE"]
    film_id: int


class CutOpDto(BaseModel):
    """Cut Op Dto.
    """
    model_config = ConfigDict(extra="ignore")

    kind: Literal["cut"]
    cutter_id: int
    operator_id: int


class DieCutOpDto(BaseModel):
    """Die Cut Op Dto.
    """
    model_config = ConfigDict(extra="ignore")

    kind: Literal["die_cut"]
    operator_id: int


RunOperationDto = Annotated[
    PrintOpDto | LaminateOpDto | CutOpDto | DieCutOpDto,
    Field(discriminator="kind"),
]


class PartDto(BaseModel):
    """Part Dto.
    """
    model_config = ConfigDict(extra="forbid")

    imposition: ImpositionDto
    count: int
    need_spacing: bool = True
    operations: tuple[RunOperationDto, ...]


class AdditionalWorkDto(BaseModel):
    """Additional Work Dto.
    """
    model_config = ConfigDict(extra="ignore")

    name: str
    price: str
    description: str
    markup: int


class ProductDto(BaseModel):
    """Product Dto.
    """
    model_config = ConfigDict(extra="ignore")

    parts_markup: int
    blocks: tuple[PartDto, ...]
    operations: tuple[AdditionalWorkDto, ...] = ()


class OrderWriteDto(BaseModel):
    """Order Write Dto.
    """
    model_config = ConfigDict(extra="ignore")

    product: ProductDto
    count: int
    description: str = ""


class OrderDto(BaseModel):
    """Order Dto.
    """
    id: int
    count: int
    description: str
    created_at: datetime
    product: ProductDto


class OrderReportDto(BaseModel):
    """Order Report Dto.
    """
    product_price: str
    order_price: str
    income: str
    impositions: tuple[int, ...]


class SaveOrderResponseDto(BaseModel):
    """Save Order Response Dto.
    """
    id: int


class ReferenceDto(BaseModel):
    """Reference Dto.
    """
    model_config = ConfigDict(extra="ignore")

    name: str
    description: str
    order_id: int


class LoginRequest(BaseModel):
    """Login Request.
    """
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token Response.
    """
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class PrinterDto(BaseModel):
    """Printer Dto.
    """
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    spacing: int
    startup: str
    cyan: str
    magenta: str
    yellow: str
    black: str


class LaminatorDto(BaseModel):
    """Laminator Dto.
    """
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    startup: str


class CutterDto(BaseModel):
    """Cutter Dto.
    """
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    max_stack: int


class OperatorDto(BaseModel):
    """Operator Dto.
    """
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    salary_by_operation: str


class PrinterWriteDto(BaseModel):
    """Printer Write Dto.
    """
    model_config = ConfigDict(extra="ignore")

    name: str
    spacing: int
    startup: str
    cyan: str
    magenta: str
    yellow: str
    black: str


class LaminatorWriteDto(BaseModel):
    """Laminator Write Dto.
    """
    model_config = ConfigDict(extra="ignore")

    name: str
    startup: str


class CutterWriteDto(BaseModel):
    """Cutter Write Dto.
    """
    model_config = ConfigDict(extra="ignore")

    name: str
    max_stack: int


class OperatorWriteDto(BaseModel):
    """Operator Write Dto.
    """
    model_config = ConfigDict(extra="ignore")

    name: str
    salary_by_operation: str
