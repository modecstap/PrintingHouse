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
from backend.new_core.chroma import Chroma, ChromaID
from backend.new_core.edges import Edges, EdgesID
from backend.new_core.values.percent import Percent
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
    ChromaDto,
    ChromaReadDto,
    EdgesDto,
    EdgesReadDto,
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


__all__ = [
    "printer_to_dto",
    "printer_from_dto",
    "printer_from_write_dto",
    "laminator_to_dto",
    "laminator_from_dto",
    "laminator_from_write_dto",
    "cutter_to_dto",
    "cutter_from_dto",
    "cutter_from_write_dto",
    "operator_to_dto",
    "press_operator_from_dto",
    "operator_from_write_dto",
    "laminator_operator_from_dto",
    "cutter_operator_from_dto",
    "die_cut_operator_from_dto",
    "printer_replace_from_dto",
    "laminator_replace_from_dto",
    "cutter_replace_from_dto",
    "press_operator_replace_from_dto",
    "laminator_operator_replace_from_dto",
    "cutter_operator_replace_from_dto",
    "die_cut_operator_replace_from_dto",
    "film_to_read_dto",
    "film_from_write_dto",
    "film_replace_from_dto",
    "sheet_to_read_dto",
    "sheet_from_write_dto",
    "sheet_replace_from_dto",
    "sheet_from_read_dto",
    "edges_to_read_dto",
    "edges_from_write_dto",
    "edges_replace_from_dto",
    "edges_from_read_dto",
    "chroma_to_read_dto",
    "chroma_from_write_dto",
    "chroma_replace_from_dto",
    "chroma_from_read_dto",
]

def _money(amount: str) -> Money:
    """Handles money.

    :param amount: the amount.

    :return: the Money result.
    """
    return Money(Decimal(amount))


def printer_to_dto(printer: Printer) -> PrinterDto:
    """Handles printer to dto.

    :param printer: the printer.

    :return: the PrinterDto result.
    """
    return PrinterDto(
        id=printer.id.value,
        name=printer.name,
        startup=str(printer.prices.startup.amount),
        cyan=str(printer.prices.cyan.amount),
        magenta=str(printer.prices.magenta.amount),
        yellow=str(printer.prices.yellow.amount),
        black=str(printer.prices.black.amount),
    )


def printer_from_dto(dto: PrinterDto) -> Printer:
    """Handles printer from dto.

    :param dto: the dto.

    :return: the Printer result.
    """
    return Printer(
        id=PrinterID(dto.id),
        name=dto.name,
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
) -> tuple[str, PrinterPrices]:
    """Handles printer from write dto.

    :param dto: the dto.

    :return: the tuple[str, PrinterPrices] result.
    """
    return (
        dto.name,
        PrinterPrices(
            startup=_money(dto.startup),
            cyan=_money(dto.cyan),
            magenta=_money(dto.magenta),
            yellow=_money(dto.yellow),
            black=_money(dto.black),
        ),
    )


def laminator_to_dto(laminator: Laminator) -> LaminatorDto:
    """Handles laminator to dto.

    :param laminator: the laminator.

    :return: the LaminatorDto result.
    """
    return LaminatorDto(
        id=laminator.id.value,
        name=laminator.name,
        startup=str(laminator.startup.amount),
    )


def laminator_from_dto(dto: LaminatorDto) -> Laminator:
    """Handles laminator from dto.

    :param dto: the dto.

    :return: the Laminator result.
    """
    return Laminator(
        id=LaminatorID(dto.id),
        name=dto.name,
        startup=_money(dto.startup),
    )


def laminator_from_write_dto(dto: LaminatorWriteDto) -> tuple[str, Money]:
    """Handles laminator from write dto.

    :param dto: the dto.

    :return: the tuple[str, Money] result.
    """
    return dto.name, _money(dto.startup)


def cutter_to_dto(cutter: Cutter) -> CutterDto:
    """Handles cutter to dto.

    :param cutter: the cutter.

    :return: the CutterDto result.
    """
    return CutterDto(
        id=cutter.id.value,
        name=cutter.name,
        max_stack=cutter.max_stack)


def cutter_from_dto(dto: CutterDto) -> Cutter:
    """Handles cutter from dto.

    :param dto: the dto.

    :return: the Cutter result.
    """
    return Cutter(id=CutterID(dto.id), name=dto.name, max_stack=dto.max_stack)


def cutter_from_write_dto(dto: CutterWriteDto) -> tuple[str, int]:
    """Handles cutter from write dto.

    :param dto: the dto.

    :return: the tuple[str, int] result.
    """
    return dto.name, dto.max_stack


def operator_to_dto(operator: PressOperator | LaminatorOperator |
                    CutterOperator | DieCutterOperator) -> OperatorDto:
    """Handles operator to dto.

    :param operator: the operator.

    :return: the OperatorDto result.
    """
    return OperatorDto(
        id=operator.id.value,
        name=operator.name,
        salary_by_operation=str(operator.salary_by_operation.amount),
    )


def press_operator_from_dto(dto: OperatorDto) -> PressOperator:
    """Handles press operator from dto.

    :param dto: the dto.

    :return: the PressOperator result.
    """
    return PressOperator(
        id=PressOperatorID(dto.id),
        name=dto.name,
        salary_by_operation=_money(dto.salary_by_operation),
    )


def operator_from_write_dto(dto: OperatorWriteDto) -> tuple[str, Money]:
    """Handles operator from write dto.

    :param dto: the dto.

    :return: the tuple[str, Money] result.
    """
    return dto.name, _money(dto.salary_by_operation)


def laminator_operator_from_dto(dto: OperatorDto) -> LaminatorOperator:
    """Handles laminator operator from dto.

    :param dto: the dto.

    :return: the LaminatorOperator result.
    """
    return LaminatorOperator(
        id=LaminatorOperatorID(dto.id),
        name=dto.name,
        salary_by_operation=_money(dto.salary_by_operation),
    )


def cutter_operator_from_dto(dto: OperatorDto) -> CutterOperator:
    """Handles cutter operator from dto.

    :param dto: the dto.

    :return: the CutterOperator result.
    """
    return CutterOperator(
        id=CutterOperatorID(dto.id),
        name=dto.name,
        salary_by_operation=_money(dto.salary_by_operation),
    )


def die_cut_operator_from_dto(dto: OperatorDto) -> DieCutterOperator:
    """Handles die cut operator from dto.

    :param dto: the dto.

    :return: the DieCutterOperator result.
    """
    return DieCutterOperator(
        id=DieCutterOperatorID(dto.id),
        name=dto.name,
        salary_by_operation=_money(dto.salary_by_operation),
    )


def printer_replace_from_dto(printer_id: int, dto: PrinterDto) -> Printer:
    """Handles printer replace from dto.

    :param printer_id: id of the printer.
    :param dto: the dto.

    :return: the Printer result.
    """
    parsed = printer_from_dto(dto)
    return replace(parsed, id=PrinterID(printer_id))


def laminator_replace_from_dto(
        laminator_id: int,
        dto: LaminatorDto) -> Laminator:
    """Handles laminator replace from dto.

    :param laminator_id: id of the laminator.
    :param dto: the dto.

    :return: the Laminator result.
    """
    parsed = laminator_from_dto(dto)
    return replace(parsed, id=LaminatorID(laminator_id))


def cutter_replace_from_dto(cutter_id: int, dto: CutterDto) -> Cutter:
    """Handles cutter replace from dto.

    :param cutter_id: id of the cutter.
    :param dto: the dto.

    :return: the Cutter result.
    """
    parsed = cutter_from_dto(dto)
    return replace(parsed, id=CutterID(cutter_id))


def press_operator_replace_from_dto(
        operator_id: int,
        dto: OperatorDto) -> PressOperator:
    """Handles press operator replace from dto.

    :param operator_id: id of the operator.
    :param dto: the dto.

    :return: the PressOperator result.
    """
    parsed = press_operator_from_dto(dto)
    return replace(parsed, id=PressOperatorID(operator_id))


def laminator_operator_replace_from_dto(
    operator_id: int,
    dto: OperatorDto,
) -> LaminatorOperator:
    """Handles laminator operator replace from dto.

    :param operator_id: id of the operator.
    :param dto: the dto.

    :return: the LaminatorOperator result.
    """
    parsed = laminator_operator_from_dto(dto)
    return replace(parsed, id=LaminatorOperatorID(operator_id))


def cutter_operator_replace_from_dto(
        operator_id: int,
        dto: OperatorDto) -> CutterOperator:
    """Handles cutter operator replace from dto.

    :param operator_id: id of the operator.
    :param dto: the dto.

    :return: the CutterOperator result.
    """
    parsed = cutter_operator_from_dto(dto)
    return replace(parsed, id=CutterOperatorID(operator_id))


def die_cut_operator_replace_from_dto(
    operator_id: int,
    dto: OperatorDto,
) -> DieCutterOperator:
    """Handles die cut operator replace from dto.

    :param operator_id: id of the operator.
    :param dto: the dto.

    :return: the DieCutterOperator result.
    """
    parsed = die_cut_operator_from_dto(dto)
    return replace(parsed, id=DieCutterOperatorID(operator_id))


def film_to_read_dto(film: Film) -> FilmReadDto:
    """Handles film to read dto.

    :param film: the film.

    :return: the FilmReadDto result.
    """
    return FilmReadDto(
        id=film.id.value,
        name=film.name,
        price=str(film.price.amount),
        density=film.density.value,
    )


def film_from_write_dto(dto: FilmDto) -> tuple[str, Money, int]:
    """Handles film from write dto.

    :param dto: the dto.

    :return: the tuple[str, Money, int] result.
    """
    return dto.name, _money(dto.price), dto.density


def film_replace_from_dto(film_id: int, dto: FilmDto) -> Film:
    """Handles film replace from dto.

    :param film_id: id of the film.
    :param dto: the dto.

    :return: the Film result.
    """
    name, price, density = film_from_write_dto(dto)
    return Film(
        id=FilmID(film_id),
        name=name,
        price=price,
        density=FilmDensity(density),
    )


def _format_from_dto(dto: FormatDto) -> Format:
    """Handles format from dto.

    :param dto: the dto.

    :return: the Format result.
    """
    return Format(name=dto.name, height=dto.height, width=dto.width)


def _format_to_dto(fmt: Format) -> FormatDto:
    """Handles format to dto.

    :param fmt: the fmt.

    :return: the FormatDto result.
    """
    return FormatDto(name=fmt.name, height=fmt.height, width=fmt.width)


def sheet_to_read_dto(sheet: Sheet) -> SheetReadDto:
    """Handles sheet to read dto.

    :param sheet: the sheet.

    :return: the SheetReadDto result.
    """
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
    """Handles sheet from write dto.

    :param dto: the dto.

    :return: the tuple[Paper, Format] result.
    """
    paper = Paper(
        density=PaperDensity(dto.paper.density),
        thickness=dto.paper.thickness,
        type=PaperType(dto.paper.name),
        price_per_kilo=_money(dto.paper.price_per_kilo),
    )
    return paper, _format_from_dto(dto.format)


def sheet_replace_from_dto(sheet_id: int, dto: SheetDto) -> Sheet:
    """Handles sheet replace from dto.

    :param sheet_id: id of the sheet.
    :param dto: the dto.

    :return: the Sheet result.
    """
    paper, sheet_format = sheet_from_write_dto(dto)
    return Sheet(id=SheetID(sheet_id), paper=paper, format=sheet_format)


def sheet_from_read_dto(dto: SheetReadDto) -> Sheet:
    """Builds a domain sheet from a read DTO (id + paper + format).

    :param dto: the dto.

    :return: the Sheet result.
    """
    paper, sheet_format = sheet_from_write_dto(
        SheetDto(paper=dto.paper, format=dto.format),
    )
    return Sheet(id=SheetID(dto.id), paper=paper, format=sheet_format)


def edges_to_read_dto(edges: Edges) -> EdgesReadDto:
    """Handles edges to read dto.

    :param edges: the edges row.

    :return: the EdgesReadDto result.
    """
    return EdgesReadDto(
        id=edges.id.value,
        name=edges.name,
        bleeds=edges.bleeds,
        spacing=edges.spacing,
    )


def edges_from_write_dto(dto: EdgesDto) -> tuple[str, int, int]:
    """Handles edges from write dto.

    :param dto: the dto.

    :return: the tuple[str, int, int] result.
    """
    return dto.name, dto.bleeds, dto.spacing


def edges_replace_from_dto(edges_id: int, dto: EdgesDto) -> Edges:
    """Handles edges replace from dto.

    :param edges_id: id of the edges row.
    :param dto: the dto.

    :return: the Edges result.
    """
    name, bleeds, spacing = edges_from_write_dto(dto)
    return Edges(
        id=EdgesID(edges_id),
        name=name,
        bleeds=bleeds,
        spacing=spacing,
    )


def edges_from_read_dto(dto: EdgesReadDto) -> Edges:
    """Builds domain edges from a read DTO.

    :param dto: the dto.

    :return: the Edges result.
    """
    return Edges(
        id=EdgesID(dto.id),
        name=dto.name,
        bleeds=dto.bleeds,
        spacing=dto.spacing,
    )


def chroma_to_read_dto(chroma: Chroma) -> ChromaReadDto:
    """Maps a domain chroma row to a read DTO.

    :param chroma: the chroma row.

    :return: the ChromaReadDto result.
    """
    return ChromaReadDto(
        id=chroma.id.value,
        name=chroma.name,
        cyan=chroma.cyan.value,
        magenta=chroma.magenta.value,
        yellow=chroma.yellow.value,
        black=chroma.black.value,
    )


def chroma_from_write_dto(
    dto: ChromaDto,
) -> tuple[str, int, int, int, int]:
    """Extracts write payload fields for chroma catalog create.

    :param dto: the dto.

    :return: name and four fill ints.
    """
    return dto.name, dto.cyan, dto.magenta, dto.yellow, dto.black


def chroma_replace_from_dto(chroma_id: int, dto: ChromaDto) -> Chroma:
    """Builds a domain chroma for replace from a write DTO.

    :param chroma_id: id of the chroma row.
    :param dto: the dto.

    :return: the Chroma result.
    """
    name, cyan, magenta, yellow, black = chroma_from_write_dto(dto)
    return Chroma(
        id=ChromaID(chroma_id),
        name=name,
        cyan=Percent(cyan),
        magenta=Percent(magenta),
        yellow=Percent(yellow),
        black=Percent(black),
    )


def chroma_from_read_dto(dto: ChromaReadDto) -> Chroma:
    """Builds domain chroma from a read DTO.

    :param dto: the dto.

    :return: the Chroma result.
    """
    return Chroma(
        id=ChromaID(dto.id),
        name=dto.name,
        cyan=Percent(dto.cyan),
        magenta=Percent(dto.magenta),
        yellow=Percent(dto.yellow),
        black=Percent(dto.black),
    )
