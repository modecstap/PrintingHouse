from backend.aggregate.printer.events import Filled, Printed
from backend.aggregate.printer.money import Money
from backend.aggregate.printer.printer import Printer
from backend.aggregate.printer.values.chroma import Chroma
from backend.aggregate.printer.values.colors import Color


class PrinterService:
    def __init__(self, printer: Printer) -> None:
        """Держит переданный принтер.

        Побочные эффекты: список событий сервиса пуст.
        """
        self.printer = printer
        self.events: list[Printed | Filled] = []

    def print(self, chroma: Chroma, sheet_count: int) -> None:
        """Печатает на принтере и переносит событие в список сервиса.

        Ошибки: ошибки Printer.print проходят к вызывающему. При ошибке
        список events не меняется.
        Побочные эффекты: при успехе одно событие в конце events,
        а pending_events пуст.
        """
        self.printer.print(chroma, sheet_count)
        self.events.extend(self.printer.pull_events())

    def fill(self, color: Color, sheet_count: int, price: Money) -> None:
        """Заправляет один цвет и переносит событие в список сервиса.

        Ошибки: ошибки Printer.fill проходят к вызывающему. При ошибке
        список events не меняется.
        Побочные эффекты: при успехе одно событие в конце events,
        а pending_events пуст.
        """
        self.printer.fill(color, sheet_count, price)
        self.events.extend(self.printer.pull_events())
