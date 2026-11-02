from dataclasses import dataclass

from backend.core.order import List
from backend.core.workplaces.printing.models import PressSheet


@dataclass(frozen=True)
class SheetPlacement:
    items_per_sheet: int
    cut_count: int


def place_on_sheet(press_sheet: PressSheet, item: List) -> SheetPlacement:
    """Counts the number of items on the sheet and the number of cuts.

    :param press_sheet:
    :param item: the item cell side is not zero.

    :return: a SheetPlacement. items_per_sheet is the number of items.
    cut_count is the number of cuts. Zero items is returned as 0.
    """
    usable_width = press_sheet.width - 2 * press_sheet.spacing
    usable_height = press_sheet.height - 2 * press_sheet.spacing
    item_width = item.width + 2 * item.bleeds
    item_height = item.height + 2 * item.bleeds

    straight_x = usable_width // item_width
    straight_y = usable_height // item_height
    turned_x = usable_width // item_height
    turned_y = usable_height // item_width

    straight_items = straight_x * straight_y
    turned_items = turned_x * turned_y
    if straight_items > turned_items:
        count_x, count_y = straight_x, straight_y
    else:
        count_x, count_y = turned_x, turned_y

    items_per_sheet = count_x * count_y
    cut_count = (max(0, count_x - 1) + max(0, count_y - 1)) * 2 + 4
    return SheetPlacement(items_per_sheet=items_per_sheet, cut_count=cut_count)
