from decimal import Decimal

import pytest

from backend.aggregate.printer.errors import (
    InsufficientInkException,
    InvalidPriceException,
    InvalidSheetCountException,
)
from backend.aggregate.printer.events import Filled, Printed
from backend.aggregate.printer.money import Money
from backend.aggregate.printer.printer import Printer
from backend.aggregate.printer.printing import Printing
from backend.aggregate.printer.service import PrinterService
from backend.aggregate.printer.values.chroma import Chroma
from backend.aggregate.printer.values.colors import Color
from backend.aggregate.printer.values.ink import Ink
from backend.aggregate.printer.values.printer_id import PrinterID
from backend.aggregate.printer.values.printing_id import PrintingID


def service_with(
        *,
        printer_id: int,
        cyan: tuple[int, str],
        magenta: tuple[int, str],
        yellow: tuple[int, str],
        black: tuple[int, str],
) -> PrinterService:
    def cartridge(sheet_remains: int, amount_text: str) -> Ink:
        return Ink(sheet_remains, Money(Decimal(amount_text)))

    printer = Printer(
        PrinterID(printer_id),
        cartridge(*cyan),
        cartridge(*magenta),
        cartridge(*yellow),
        cartridge(*black),
    )
    return PrinterService(printer)


def test_print_four_one_records_toner_and_moves_event_to_service():
    service = service_with(
        printer_id=1,
        cyan=(100, "5"),
        magenta=(100, "5"),
        yellow=(100, "5"),
        black=(100, "5"),
    )

    service.print(Chroma.FOUR_ONE, 10)

    assert service.printer.printings == [
        Printing(PrintingID(1), Chroma.FOUR_ONE, 10, 10, 10, 10, 20),
    ]
    assert service.printer.cyan.sheet_remains == 90
    assert service.printer.magenta.sheet_remains == 90
    assert service.printer.yellow.sheet_remains == 90
    assert service.printer.black.sheet_remains == 80
    assert service.printer.cyan.price == Money(Decimal("5"))
    assert service.printer.magenta.price == Money(Decimal("5"))
    assert service.printer.yellow.price == Money(Decimal("5"))
    assert service.printer.black.price == Money(Decimal("5"))
    assert service.printer.id == PrinterID(1)
    assert service.events == [
        Printed(Chroma.FOUR_ONE, 10, 10, 10, 10, 20),
    ]
    assert service.printer.pending_events == []
    assert service.printer.pending_events == []


def test_print_zero_zero_records_zero_toner_and_keeps_remains():
    service = service_with(
        printer_id=1,
        cyan=(40, "2"),
        magenta=(40, "2"),
        yellow=(40, "2"),
        black=(40, "2"),
    )

    service.print(Chroma.ZERO_ZERO, 10)

    assert service.printer.cyan.sheet_remains == 40
    assert service.printer.magenta.sheet_remains == 40
    assert service.printer.yellow.sheet_remains == 40
    assert service.printer.black.sheet_remains == 40
    assert service.printer.cyan.price == Money(Decimal("2"))
    assert service.printer.magenta.price == Money(Decimal("2"))
    assert service.printer.yellow.price == Money(Decimal("2"))
    assert service.printer.black.price == Money(Decimal("2"))
    assert service.printer.printings == [
        Printing(PrintingID(1), Chroma.ZERO_ZERO, 10, 0, 0, 0, 0),
    ]
    assert service.events == [
        Printed(Chroma.ZERO_ZERO, 10, 0, 0, 0, 0),
    ]
    assert service.printer.pending_events == []


@pytest.mark.parametrize(
    (
        "chroma",
        "cyan_remains",
        "magenta_remains",
        "yellow_remains",
        "black_remains",
        "cyan",
        "magenta",
        "yellow",
        "black",
    ),
    [
        (Chroma.ONE_ZERO, 100, 100, 100, 90, 0, 0, 0, 10),
        (Chroma.ONE_ONE, 100, 100, 100, 80, 0, 0, 0, 20),
        (Chroma.FOUR_ZERO, 90, 90, 90, 90, 10, 10, 10, 10),
        (Chroma.FOUR_FOUR, 80, 80, 80, 80, 20, 20, 20, 20),
    ],
)
def test_print_consumes_toner_for_remaining_chromas(
        chroma,
        cyan_remains,
        magenta_remains,
        yellow_remains,
        black_remains,
        cyan,
        magenta,
        yellow,
        black,
):
    service = service_with(
        printer_id=1,
        cyan=(100, "1"),
        magenta=(100, "1"),
        yellow=(100, "1"),
        black=(100, "1"),
    )

    service.print(chroma, 10)

    assert service.printer.cyan.sheet_remains == cyan_remains
    assert service.printer.magenta.sheet_remains == magenta_remains
    assert service.printer.yellow.sheet_remains == yellow_remains
    assert service.printer.black.sheet_remains == black_remains
    assert service.events == [
        Printed(chroma, 10, cyan, magenta, yellow, black),
    ]


def test_print_four_one_changes_nothing_when_black_is_short():
    service = service_with(
        printer_id=1,
        cyan=(100, "5"),
        magenta=(100, "5"),
        yellow=(100, "5"),
        black=(19, "5"),
    )

    with pytest.raises(InsufficientInkException):
        service.print(Chroma.FOUR_ONE, 10)

    assert service.printer.cyan.sheet_remains == 100
    assert service.printer.magenta.sheet_remains == 100
    assert service.printer.yellow.sheet_remains == 100
    assert service.printer.black.sheet_remains == 19
    assert service.printer.cyan.price == Money(Decimal("5"))
    assert service.printer.magenta.price == Money(Decimal("5"))
    assert service.printer.yellow.price == Money(Decimal("5"))
    assert service.printer.black.price == Money(Decimal("5"))
    assert service.printer.printings == []
    assert service.events == []
    assert service.printer.pending_events == []


def test_print_one_zero_consumes_black_when_cyan_is_empty():
    service = service_with(
        printer_id=1,
        cyan=(0, "5"),
        magenta=(100, "5"),
        yellow=(100, "5"),
        black=(100, "5"),
    )

    service.print(Chroma.ONE_ZERO, 10)

    assert service.printer.cyan.sheet_remains == 0
    assert service.printer.magenta.sheet_remains == 100
    assert service.printer.yellow.sheet_remains == 100
    assert service.printer.black.sheet_remains == 90
    assert service.events == [
        Printed(Chroma.ONE_ZERO, 10, 0, 0, 0, 10),
    ]


def test_print_four_one_succeeds_when_each_color_exactly_covers_consumption():
    service = service_with(
        printer_id=1,
        cyan=(10, "5"),
        magenta=(10, "5"),
        yellow=(10, "5"),
        black=(20, "5"),
    )

    service.print(Chroma.FOUR_ONE, 10)

    assert service.printer.cyan.sheet_remains == 0
    assert service.printer.magenta.sheet_remains == 0
    assert service.printer.yellow.sheet_remains == 0
    assert service.printer.black.sheet_remains == 0
    assert service.printer.printings == [
        Printing(PrintingID(1), Chroma.FOUR_ONE, 10, 10, 10, 10, 20),
    ]
    assert service.events == [
        Printed(Chroma.FOUR_ONE, 10, 10, 10, 10, 20),
    ]


def test_print_one_zero_uses_the_last_black_sheet():
    service = service_with(
        printer_id=1,
        cyan=(1, "1"),
        magenta=(1, "1"),
        yellow=(1, "1"),
        black=(1, "1"),
    )

    service.print(Chroma.ONE_ZERO, 1)

    assert service.printer.black.sheet_remains == 0
    assert service.printer.cyan.sheet_remains == 1
    assert service.printer.magenta.sheet_remains == 1
    assert service.printer.yellow.sheet_remains == 1
    assert service.printer.printings == [
        Printing(PrintingID(1), Chroma.ONE_ZERO, 1, 0, 0, 0, 1),
    ]


def test_fill_replaces_one_color_and_appends_two_events():
    service = service_with(
        printer_id=1,
        cyan=(5, "3"),
        magenta=(6, "4"),
        yellow=(7, "5"),
        black=(8, "6"),
    )

    service.fill(Color.BLACK, 100, Money(Decimal("50")))
    service.fill(Color.BLACK, 40, Money(Decimal("20")))

    assert service.printer.black.sheet_remains == 40
    assert service.printer.black.price == Money(Decimal("20"))
    assert service.printer.cyan.sheet_remains == 5
    assert service.printer.cyan.price == Money(Decimal("3"))
    assert service.printer.magenta.sheet_remains == 6
    assert service.printer.magenta.price == Money(Decimal("4"))
    assert service.printer.yellow.sheet_remains == 7
    assert service.printer.yellow.price == Money(Decimal("5"))
    assert service.printer.printings == []
    assert service.events == [
        Filled(Color.BLACK, 100, Money(Decimal("50"))),
        Filled(Color.BLACK, 40, Money(Decimal("20"))),
    ]
    assert service.printer.pending_events == []


def test_rejected_print_between_two_prints_keeps_earlier_service_event():
    service = service_with(
        printer_id=1,
        cyan=(100, "5"),
        magenta=(100, "5"),
        yellow=(100, "5"),
        black=(20, "5"),
    )

    service.print(Chroma.ONE_ZERO, 1)
    with pytest.raises(InsufficientInkException):
        service.print(Chroma.FOUR_ONE, 10)
    service.print(Chroma.ONE_ZERO, 2)

    assert service.events == [
        Printed(Chroma.ONE_ZERO, 1, 0, 0, 0, 1),
        Printed(Chroma.ONE_ZERO, 2, 0, 0, 0, 2),
    ]
    assert service.printer.printings == [
        Printing(PrintingID(1), Chroma.ONE_ZERO, 1, 0, 0, 0, 1),
        Printing(PrintingID(2), Chroma.ONE_ZERO, 2, 0, 0, 0, 2),
    ]
    assert service.printer.pending_events == []


def test_fill_does_not_consume_printing_id():
    service = service_with(
        printer_id=1,
        cyan=(50, "5"),
        magenta=(50, "5"),
        yellow=(50, "5"),
        black=(50, "5"),
    )

    service.fill(Color.BLACK, 40, Money(Decimal("9")))
    service.print(Chroma.ONE_ZERO, 10)

    assert service.printer.printings == [
        Printing(PrintingID(1), Chroma.ONE_ZERO, 10, 0, 0, 0, 10),
    ]
    assert service.printer.black.sheet_remains == 30
    assert service.events == [
        Filled(Color.BLACK, 40, Money(Decimal("9"))),
        Printed(Chroma.ONE_ZERO, 10, 0, 0, 0, 10),
    ]


@pytest.mark.parametrize("sheet_count", [0, -1, True, 1.5])
def test_print_rejects_sheet_count_below_one(sheet_count):
    service = service_with(
        printer_id=1,
        cyan=(30, "5"),
        magenta=(30, "5"),
        yellow=(30, "5"),
        black=(30, "5"),
    )

    with pytest.raises(InvalidSheetCountException):
        service.print(Chroma.ONE_ZERO, sheet_count)

    assert service.printer.black.sheet_remains == 30
    assert service.printer.printings == []
    assert service.events == []
    assert service.printer.pending_events == []


@pytest.mark.parametrize("sheet_count", [0, -1])
def test_fill_rejects_non_positive_sheet_count(sheet_count):
    service = service_with(
        printer_id=1,
        cyan=(8, "6"),
        magenta=(8, "6"),
        yellow=(8, "6"),
        black=(8, "6"),
    )

    with pytest.raises(InvalidSheetCountException):
        service.fill(Color.BLACK, sheet_count, Money(Decimal("10")))

    assert service.printer.black.sheet_remains == 8
    assert service.printer.black.price == Money(Decimal("6"))
    assert service.printer.printings == []
    assert service.events == []
    assert service.printer.pending_events == []


def test_fill_rejects_zero_price():
    service = service_with(
        printer_id=1,
        cyan=(8, "6"),
        magenta=(8, "6"),
        yellow=(8, "6"),
        black=(8, "6"),
    )

    with pytest.raises(InvalidPriceException):
        service.fill(Color.BLACK, 10, Money(Decimal("0")))

    assert service.printer.black.sheet_remains == 8
    assert service.printer.black.price == Money(Decimal("6"))
    assert service.printer.printings == []
    assert service.events == []
    assert service.printer.pending_events == []
