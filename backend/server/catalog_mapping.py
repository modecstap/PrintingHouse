"""Maps equipment and staff catalog rows to JSON DTOs."""

from __future__ import annotations

from decimal import Decimal

from backend.new_core.format import Format
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
from backend.new_core.materials.film import Film, FilmID
from backend.new_core.materials.paper import Paper
from backend.new_core.materials.sheet import Sheet, SheetID
from backend.new_core.personal.press_operator import PressOperator, PressOperatorID
from backend.new_core.values.money import Money
from backend.server.schemas import (
    CutterDto,
    FilmDto,
    FilmReadDto,
    FormatDto,
    LaminatorDto,
    OperatorDto,
    PaperDto,
    PrinterDto,
    SheetDto,
    SheetReadDto,
)


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


def film_to_read_dto(film: Film) -> FilmReadDto:
    return FilmReadDto(
        id=film.id.value,
        name=film.name,
        price=str(film.price.amount),
        density=film.density,
    )


def film_from_write_dto(dto: FilmDto) -> tuple[str, Money, int]:
    return dto.name, _money(dto.price), dto.density


def film_replace_from_dto(film_id: int, dto: FilmDto) -> Film:
    name, price, density = film_from_write_dto(dto)
    return Film(id=FilmID(film_id), name=name, price=price, density=density)


def _format_from_dto(dto: FormatDto) -> Format:
    return Format(name=dto.name, height=dto.height, width=dto.width)


def _format_to_dto(fmt: Format) -> FormatDto:
    return FormatDto(name=fmt.name, height=fmt.height, width=fmt.width)


def sheet_to_read_dto(sheet: Sheet) -> SheetReadDto:
    return SheetReadDto(
        id=sheet.id.value,
        paper=PaperDto(
            density=sheet.paper.density,
            thickness=sheet.paper.thickness,
            name=sheet.paper.name,
            price_per_kilo=str(sheet.paper.price_per_kilo.amount),
        ),
        format=_format_to_dto(sheet.format),
    )


def sheet_from_write_dto(dto: SheetDto) -> tuple[Paper, Format]:
    paper = Paper(
        density=dto.paper.density,
        thickness=dto.paper.thickness,
        name=dto.paper.name,
        price_per_kilo=_money(dto.paper.price_per_kilo),
    )
    return paper, _format_from_dto(dto.format)


def sheet_replace_from_dto(sheet_id: int, dto: SheetDto) -> Sheet:
    paper, format = sheet_from_write_dto(dto)
    return Sheet(id=SheetID(sheet_id), paper=paper, format=format)
