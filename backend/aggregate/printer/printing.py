from backend.aggregate.printer.values.ink import Ink
from backend.aggregate.printer.values.printing_id import PrintingID


class Printing:
    def __init__(self):
        self._id: PrintingID
        self._sheet_count: int
        self._used_cyan: Ink
        self._used_magenta: Ink
        self._used_yellow: Ink
        self._used_black: Ink

    def cost(self):
        pass