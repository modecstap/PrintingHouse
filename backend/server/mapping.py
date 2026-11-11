"""Maps JSON DTOs to domain objects and back."""

from __future__ import annotations

from decimal import Decimal

from backend.new_core.accountant.order_report import OrderReport
from backend.new_core.format import Format
from backend.new_core.materials.film import FilmID
from backend.new_core.materials.sheet import SheetID
from backend.new_core.operations.cut.cut import Cut
from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.operations.laminate.laminate import Laminate
from backend.new_core.operations.laminate.lamination import Lamination
from backend.new_core.operations.print.chroma import Chroma
from backend.new_core.operations.print.print import Print
from backend.new_core.operations.run_operation import RunOperation
from backend.new_core.order.additional_work import AdditionalWork
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.product import Product
from backend.new_core.part import Part
from backend.new_core.print_run.imposition import Imposition
from backend.new_core.reference.reference import Reference
from backend.new_core.values.money import Money
from backend.new_core.values.percent import Percent
from backend.new_core.equipment.cutter import CutterID
from backend.new_core.equipment.laminator import LaminatorID
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.personal.cutter_operator import CutterOperatorID
from backend.new_core.personal.die_cutter_operator import DieCutterOperatorID
from backend.new_core.personal.laminator_operator import LaminatorOperatorID
from backend.new_core.personal.press_operator import PressOperatorID
from backend.server.schemas import (
    AdditionalWorkDto,
    CutOpDto,
    DieCutOpDto,
    FormatDto,
    ImpositionDto,
    LaminateOpDto,
    OrderDto,
    OrderReportDto,
    PartDto,
    PrintOpDto,
    ProductDto,
    ReferenceDto,
    RunOperationDto,
)


def _money_from_str(value: str) -> Money:
    return Money(Decimal(value))


def _money_to_str(value: Money) -> str:
    return format(value.amount, "f")


def _format_from_dto(dto: FormatDto) -> Format:
    return Format(name=dto.name, height=dto.height, width=dto.width)


def _imposition_from_dto(dto: ImpositionDto) -> Imposition:
    return Imposition(
        target=_format_from_dto(dto.target),
        sheet_id=SheetID(dto.sheet_id),
        press_sheet=None,
        bleeds=dto.bleeds,
        spacing=dto.spacing,
    )


def _operation_from_dto(dto: RunOperationDto) -> RunOperation:
    if isinstance(dto, PrintOpDto):
        return Print(
            printer_id=PrinterID(dto.printer_id),
            operator_id=PressOperatorID(dto.operator_id),
            chroma=Chroma[dto.chroma],
        )
    if isinstance(dto, LaminateOpDto):
        return Laminate(
            laminator_id=LaminatorID(dto.laminator_id),
            operator_id=LaminatorOperatorID(dto.operator_id),
            lamination=Lamination[dto.lamination],
            film_id=FilmID(dto.film_id),
        )
    if isinstance(dto, CutOpDto):
        return Cut(
            cutter_id=CutterID(dto.cutter_id),
            operator_id=CutterOperatorID(dto.operator_id),
        )
    if isinstance(dto, DieCutOpDto):
        return DieCut(operator_id=DieCutterOperatorID(dto.operator_id))
    raise TypeError(f"unknown operation dto: {type(dto)!r}")


def _part_from_dto(dto: PartDto) -> Part:
    return Part(
        imposition=_imposition_from_dto(dto.imposition),
        count=dto.count,
        operations=tuple(_operation_from_dto(op) for op in dto.operations),
    )


def _additional_work_from_dto(dto: AdditionalWorkDto) -> AdditionalWork:
    return AdditionalWork(
        name=dto.name,
        price=_money_from_str(dto.price),
        description=dto.description,
        markup=Percent(dto.markup),
    )


def product_from_dto(dto: ProductDto) -> Product:
    """Builds a domain product from JSON.

    :param dto:

    :return: ``Product`` instance.
    """
    return Product(
        parts_markup=Percent(dto.parts_markup),
        blocks=tuple(_part_from_dto(block) for block in dto.blocks),
        operations=tuple(_additional_work_from_dto(op) for op in dto.operations),
    )


def _format_to_dto(fmt: Format) -> FormatDto:
    return FormatDto(name=fmt.name, height=fmt.height, width=fmt.width)


def _imposition_to_dto(imposition: Imposition) -> ImpositionDto:
    return ImpositionDto(
        target=_format_to_dto(imposition.target),
        sheet_id=imposition.sheet_id.value,
        bleeds=imposition.bleeds,
        spacing=imposition.spacing,
    )


def _operation_to_dto(operation: RunOperation) -> RunOperationDto:
    if isinstance(operation, Print):
        return PrintOpDto(
            kind="print",
            printer_id=operation.printer_id.value,
            operator_id=operation.operator_id.value,
            chroma=operation.chroma.name,
        )
    if isinstance(operation, Laminate):
        return LaminateOpDto(
            kind="laminate",
            laminator_id=operation.laminator_id.value,
            operator_id=operation.operator_id.value,
            lamination=operation.lamination.name,
            film_id=operation.film_id.value,
        )
    if isinstance(operation, Cut):
        return CutOpDto(
            kind="cut",
            cutter_id=operation.cutter_id.value,
            operator_id=operation.operator_id.value,
        )
    if isinstance(operation, DieCut):
        return DieCutOpDto(
            kind="die_cut",
            operator_id=operation.operator_id.value,
        )
    raise TypeError(f"unsupported operation: {type(operation)!r}")


def _part_to_dto(part: Part) -> PartDto:
    return PartDto(
        imposition=_imposition_to_dto(part.imposition),
        count=part.count,
        operations=tuple(_operation_to_dto(op) for op in part.operations),
    )


def _additional_work_to_dto(work: AdditionalWork) -> AdditionalWorkDto:
    return AdditionalWorkDto(
        name=work.name,
        price=_money_to_str(work.price),
        description=work.description,
        markup=work.markup.value,
    )


def product_to_dto(product: Product) -> ProductDto:
    """Serializes a domain product to JSON.

    :param product:

    :return: DTO tree.
    """
    return ProductDto(
        parts_markup=product.parts_markup.value,
        blocks=tuple(_part_to_dto(block) for block in product.blocks),
        operations=tuple(_additional_work_to_dto(op) for op in product.operations),
    )


def order_to_dto(order: Order) -> OrderDto:
    """Serializes a stored order.

    :param order:

    :return: order JSON shape.
    """
    return OrderDto(
        id=order.id.value,
        count=order.count,
        description=order.description,
        created_at=order.created_at,
        product=product_to_dto(order.product),
    )


def report_to_dto(report: OrderReport) -> OrderReportDto:
    """Serializes an order price report.

    :param report:

    :return: report JSON shape.
    """
    return OrderReportDto(
        product_price=_money_to_str(report.product_price),
        order_price=_money_to_str(report.order_price),
        income=_money_to_str(report.income),
        impositions=report.impositions,
    )


def reference_from_dto(dto: ReferenceDto) -> Reference:
    """Builds a domain reference from JSON.

    :param dto:

    :return: ``Reference`` instance.
    """
    return Reference(
        name=dto.name,
        description=dto.description,
        order_id=OrderID(dto.order_id),
    )


def reference_to_dto(reference: Reference) -> ReferenceDto:
    """Serializes a reference row.

    :param reference:

    :return: reference JSON shape.
    """
    return ReferenceDto(
        name=reference.name,
        description=reference.description,
        order_id=reference.order_id.value,
    )
