from decimal import Decimal, ROUND_HALF_UP


class ItemCalculator:
    def __init__(
            self,
            item_count,
            sheet_cost_price,
            sheet_by_fitting,
            item_per_sheet,
            sheet_cost,
    ):
        self._item_count = item_count
        self._sheet_cost_price = sheet_cost_price
        self._sheet_by_fitting = sheet_by_fitting
        self._item_per_sheet = item_per_sheet
        self._sheet_cost = sheet_cost

    def get_item_cost(self) -> Decimal:
        item_cost = (self._sheet_cost / min(self._item_per_sheet, self._item_count))
        item_cost = item_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return item_cost

    def get_item_cost_price(self) -> Decimal:
        item_cost_price = (self._sheet_cost_price / min(self._item_per_sheet, self._item_count))
        item_cost_price = item_cost_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return item_cost_price
