from backend.aggregate.printer.money import Money
from backend.aggregate.printer.values.chroma import Chroma
from backend.aggregate.printer.values.colors import Color


class Printed:
    def __init__(
            self,
            chroma: Chroma,
            sheet_count: int,
            cyan: int,
            magenta: int,
            yellow: int,
            black: int,
    ) -> None:
        """Сохраняет событие успешной печати."""
        self.chroma = chroma
        self.sheet_count = sheet_count
        self.cyan = cyan
        self.magenta = magenta
        self.yellow = yellow
        self.black = black

    def __eq__(self, other: object) -> bool:
        if type(other) is not Printed:
            return NotImplemented
        return (
            self.chroma == other.chroma
            and self.sheet_count == other.sheet_count
            and self.cyan == other.cyan
            and self.magenta == other.magenta
            and self.yellow == other.yellow
            and self.black == other.black
        )


class Filled:
    def __init__(self, color: Color, sheet_count: int, price: Money) -> None:
        """Сохраняет событие заправки одного цвета."""
        self.color = color
        self.sheet_count = sheet_count
        self.price = price

    def __eq__(self, other: object) -> bool:
        if type(other) is not Filled:
            return NotImplemented
        return (
            self.color == other.color
            and self.sheet_count == other.sheet_count
            and self.price == other.price
        )
