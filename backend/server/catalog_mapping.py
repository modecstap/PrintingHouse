"""Maps equipment and staff catalog rows to JSON DTOs."""

from __future__ import annotations

from decimal import Decimal

from backend.new_core.equipment.cutter import Cutter, CutterID
from backend.new_core.equipment.laminator import Laminator, LaminatorID
from backend.new_core.equipment.printer import Printer, PrinterID
from backend.new_core.personal.cutter_operator import CutterOperator, CutterOperatorID
from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)
from backend.new_core.personal.press_operator import PressOperator, PressOperatorID
from backend.new_core.values.money import Money
from backend.server.schemas import CutterDto, LaminatorDto, OperatorDto, PrinterDto


def _money(amount: str) -> Money:
    return Money(Decimal(amount))


def printer_to_dto(printer: Printer) -> PrinterDto:
    return PrinterDto(
        id=printer.id.value,
        startup=str(printer.startup.amount),
        cyan=str(printer.cyan.amount),
        magenta=str(printer.magenta.amount),
        yellow=str(printer.yellow.amount),
        black=str(printer.black.amount),
    )


def printer_from_dto(dto: PrinterDto) -> Printer:
    return Printer(
        id=PrinterID(dto.id),
        startup=_money(dto.startup),
        cyan=_money(dto.cyan),
        magenta=_money(dto.magenta),
        yellow=_money(dto.yellow),
        black=_money(dto.black),
    )


def laminator_to_dto(laminator: Laminator) -> LaminatorDto:
    return LaminatorDto(
        id=laminator.id.value,
        startup=str(laminator.startup.amount),
    )


def laminator_from_dto(dto: LaminatorDto) -> Laminator:
    return Laminator(
        id=LaminatorID(dto.id),
        startup=_money(dto.startup),
    )


def cutter_to_dto(cutter: Cutter) -> CutterDto:
    return CutterDto(id=cutter.id.value, max_stack=cutter.max_stack)


def cutter_from_dto(dto: CutterDto) -> Cutter:
    return Cutter(id=CutterID(dto.id), max_stack=dto.max_stack)


def operator_to_dto(operator: PressOperator | LaminatorOperator | CutterOperator | DieCutterOperator) -> OperatorDto:
    return OperatorDto(
        id=operator.id.value,
        salary_by_operation=str(operator.salary_by_operation.amount),
    )


def press_operator_from_dto(dto: OperatorDto) -> PressOperator:
    return PressOperator(
        id=PressOperatorID(dto.id),
        salary_by_operation=_money(dto.salary_by_operation),
    )


def laminator_operator_from_dto(dto: OperatorDto) -> LaminatorOperator:
    return LaminatorOperator(
        id=LaminatorOperatorID(dto.id),
        salary_by_operation=_money(dto.salary_by_operation),
    )


def cutter_operator_from_dto(dto: OperatorDto) -> CutterOperator:
    return CutterOperator(
        id=CutterOperatorID(dto.id),
        salary_by_operation=_money(dto.salary_by_operation),
    )


def die_cut_operator_from_dto(dto: OperatorDto) -> DieCutterOperator:
    return DieCutterOperator(
        id=DieCutterOperatorID(dto.id),
        salary_by_operation=_money(dto.salary_by_operation),
    )
