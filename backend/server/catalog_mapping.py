"""Maps equipment and staff catalog rows to JSON DTOs."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from backend.new_core.format import Format
from backend.new_core.equipment.cutter import Cutter, CutterID
from backend.new_core.equipment.laminator import Laminator, LaminatorID
from backend.new_core.equipment.printer import Printer, PrinterID, PrinterPrices
from backend.new_core.personal.cutter_operator import (
    CutterOperator,
    CutterOperatorID,
)
from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)
from backend.new_core.materials.film import Film, FilmID
from backend.new_core.materials.film_density import FilmDensity
from backend.new_core.materials.paper import Paper
from backend.new_core.materials.paper_density import PaperDensity
from backend.new_core.materials.paper_type import PaperType
from backend.new_core.materials.sheet import Sheet, SheetID
from backend.new_core.personal.press_operator import (
    PressOperator,
    PressOperatorID,
)
from backend.new_core.values.money import Money
from backend.server.schemas import (
    CutterDto,
    CutterWriteDto,
    FilmDto,
    FilmReadDto,
    FormatDto,
    LaminatorDto,
    LaminatorWriteDto,
    OperatorDto,
    OperatorWriteDto,
    PaperDto,
    PrinterDto,
    PrinterWriteDto,
    SheetDto,
    SheetReadDto,
)


def _money(amount: str) -> Money:
    return Money(Decimal(amount))


def printer_to_dto(printer: Printer) -> PrinterDto:
    return PrinterDto(
        id=printer.id.value,
        name=printer.name,
        spacing=printer.spacing,
        startup=str(printer.prices.startup.amount),
        cyan=str(printer.prices.cyan.amount),
        magenta=str(printer.prices.magenta.amount),
        yellow=str(printer.prices.yellow.amount),
        black=str(printer.prices.black.amount),
    )


def printer_from_dto(dto: PrinterDto) -> Printer:
    return Printer(
        id=PrinterID(dto.id),
        name=dto.name,
        spacing=dto.spacing,
        prices=PrinterPrices(
            startup=_money(dto.startup),
            cyan=_money(dto.cyan),
            magenta=_money(dto.magenta),
            yellow=_money(dto.yellow),
            black=_money(dto.black),
        ),
    )


def printer_from_write_dto(
    dto: PrinterWriteDto,
) -> tuple[str, int, PrinterPrices]:
    return (
        dto.name,
        dto.spacing,
        PrinterPrices(
            startup=_money(dto.startup),
            cyan=_money(dto.cyan),
            magenta=_money(dto.magenta),
            yellow=_money(dto.yellow),
            black=_money(dto.black),
        ),
    )


def laminator_to_dto(laminator: Laminator) -> LaminatorDto:
    return LaminatorDto(
        id=laminator.id.value,
        name=laminator.name,
        startup=str(laminator.startup.amount),
    )


def laminator_from_dto(dto: LaminatorDto) -> Laminator:
    return Laminator(
        id=LaminatorID(dto.id),
        name=dto.name,
        startup=_money(dto.startup),
    )


def laminator_from_write_dto(dto: LaminatorWriteDto) -> tuple[str, Money]:
    return dto.name, _money(dto.startup)


def cutter_to_dto(cutter: Cutter) -> CutterDto:
    return CutterDto(
        id=cutter.id.value,
        name=cutter.name,
        max_stack=cutter.max_stack)


def cutter_from_dto(dto: CutterDto) -> Cutter:
    return Cutter(id=CutterID(dto.id), name=dto.name, max_stack=dto.max_stack)


def cutter_from_write_dto(dto: CutterWriteDto) -> tuple[str, int]:
    return dto.name, dto.max_stack


def operator_to_dto(operator: PressOperator | LaminatorOperator |
                    CutterOperator | DieCutterOperator) -> OperatorDto:
    return OperatorDto(
        id=operator.id.value,
        name=operator.name,
        salary_by_operation=str(operator.salary_by_operation.amount),
    )


def press_operator_from_dto(dto: OperatorDto) -> PressOperator:
    return PressOperator(
        id=PressOperatorID(dto.id),
        name=dto.name,
        salary_by_operation=_money(dto.salary_by_operation),
    )


def operator_from_write_dto(dto: OperatorWriteDto) -> tuple[str, Money]:
    return dto.name, _money(dto.salary_by_operation)


def laminator_operator_from_dto(dto: OperatorDto) -> LaminatorOperator:
    return LaminatorOperator(
        id=LaminatorOperatorID(dto.id),
        name=dto.name,
        salary_by_operation=_money(dto.salary_by_operation),
    )


def cutter_operator_from_dto(dto: OperatorDto) -> CutterOperator:
    return CutterOperator(
        id=CutterOperatorID(dto.id),
        name=dto.name,
        salary_by_operation=_money(dto.salary_by_operation),
    )


def die_cut_operator_from_dto(dto: OperatorDto) -> DieCutterOperator:
    return DieCutterOperator(
        id=DieCutterOperatorID(dto.id),
        name=dto.name,
        salary_by_operation=_money(dto.salary_by_operation),
    )


def printer_replace_from_dto(printer_id: int, dto: PrinterDto) -> Printer:
    parsed = printer_from_dto(dto)
    return replace(parsed, id=PrinterID(printer_id))


def laminator_replace_from_dto(
        laminator_id: int,
        dto: LaminatorDto) -> Laminator:
    parsed = laminator_from_dto(dto)
    return replace(parsed, id=LaminatorID(laminator_id))


def cutter_replace_from_dto(cutter_id: int, dto: CutterDto) -> Cutter:
    parsed = cutter_from_dto(dto)
    return replace(parsed, id=CutterID(cutter_id))


def press_operator_replace_from_dto(
        operator_id: int,
        dto: OperatorDto) -> PressOperator:
    parsed = press_operator_from_dto(dto)
    return replace(parsed, id=PressOperatorID(operator_id))


def laminator_operator_replace_from_dto(
    operator_id: int,
    dto: OperatorDto,
) -> LaminatorOperator:
    parsed = laminator_operator_from_dto(dto)
    return replace(parsed, id=LaminatorOperatorID(operator_id))


def cutter_operator_replace_from_dto(
        operator_id: int,
        dto: OperatorDto) -> CutterOperator:
    parsed = cutter_operator_from_dto(dto)
    return replace(parsed, id=CutterOperatorID(operator_id))


def die_cut_operator_replace_from_dto(
    operator_id: int,
    dto: OperatorDto,
) -> DieCutterOperator:
    parsed = die_cut_operator_from_dto(dto)
    return replace(parsed, id=DieCutterOperatorID(operator_id))


def film_to_read_dto(film: Film) -> FilmReadDto:
    return FilmReadDto(
        id=film.id.value,
        name=film.name,
        price=str(film.price.amount),
        density=film.density.value,
    )


def film_from_write_dto(dto: FilmDto) -> tuple[str, Money, int]:
    return dto.name, _money(dto.price), dto.density


def film_replace_from_dto(film_id: int, dto: FilmDto) -> Film:
    name, price, density = film_from_write_dto(dto)
    return Film(
        id=FilmID(film_id),
        name=name,
        price=price,
        density=FilmDensity(density),
    )


def _format_from_dto(dto: FormatDto) -> Format:
    return Format(name=dto.name, height=dto.height, width=dto.width)


def _format_to_dto(fmt: Format) -> FormatDto:
    return FormatDto(name=fmt.name, height=fmt.height, width=fmt.width)


def sheet_to_read_dto(sheet: Sheet) -> SheetReadDto:
    return SheetReadDto(
        id=sheet.id.value,
        paper=PaperDto(
            density=sheet.paper.density.value,
            thickness=sheet.paper.thickness,
            name=sheet.paper.type.value,
            price_per_kilo=str(sheet.paper.price_per_kilo.amount),
        ),
        format=_format_to_dto(sheet.format),
    )


def sheet_from_write_dto(dto: SheetDto) -> tuple[Paper, Format]:
    paper = Paper(
        density=PaperDensity(dto.paper.density),
        thickness=dto.paper.thickness,
        type=PaperType(dto.paper.name),
        price_per_kilo=_money(dto.paper.price_per_kilo),
    )
    return paper, _format_from_dto(dto.format)


def sheet_replace_from_dto(sheet_id: int, dto: SheetDto) -> Sheet:
    paper, sheet_format = sheet_from_write_dto(dto)
    return Sheet(id=SheetID(sheet_id), paper=paper, format=sheet_format)


def sheet_from_read_dto(dto: SheetReadDto) -> Sheet:
    """Builds a domain sheet from a read DTO (id + paper + format)."""
    paper, sheet_format = sheet_from_write_dto(
        SheetDto(paper=dto.paper, format=dto.format),
    )
    return Sheet(id=SheetID(dto.id), paper=paper, format=sheet_format)
