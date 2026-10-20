from backend.aggregate.printer.money import Money


class Ink:
    def __init__(self):
        self._sheet_remains = 0 # A3
        self._price = 0

    def fill(self, sheet_count, price: Money):
        pass
