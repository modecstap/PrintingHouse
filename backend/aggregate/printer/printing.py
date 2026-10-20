from backend.aggregate.printer.values.chroma import Chroma
from backend.aggregate.printer.values.printing_id import PrintingID


class Printing:
    def __init__(
            self,
            printing_id: PrintingID,
            chroma: Chroma,
            sheet_count: int,
            cyan: int,
            magenta: int,
            yellow: int,
            black: int,
    ) -> None:
        """Сохраняет одну запись истории печати."""
        self.id = printing_id
        self.chroma = chroma
        self.sheet_count = sheet_count
        self.cyan = cyan
        self.magenta = magenta
        self.yellow = yellow
        self.black = black
        