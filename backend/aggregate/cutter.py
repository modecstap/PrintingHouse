from backend.aggregate.printer.money import Money


class Cutter:
    def __init__(self):
        sheet_in_stack: int
        cut_price: Money

    def cut(self, placement, paper, sheet_count) -> int:
        """публикует ивент о количестве резов"""
        pass
