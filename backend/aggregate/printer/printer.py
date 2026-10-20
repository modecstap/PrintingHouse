from backend.aggregate.printer.values.colors import Color
from backend.aggregate.printer.values.ink import Ink
from backend.models import Chroma, Printing




class Printer:
    def __init__(
            self,
            cyan: Ink,
            magenta: Ink,
            yellow: Ink,
            black: Ink,
    ):
        self.id
        self.cyan = Ink()
        self.magenta = Ink()
        self.yellow = Ink()
        self.black = Ink()
        printings: list[Printing] = []

    def print(self, chroma: Chroma, sheet_count):
        """публикует ивент печати и записывает печать в историю"""
        pass

    def fill(self, color: Color, sheet_count: int, price):
        """заполнят соответствующий цвет"""
        pass