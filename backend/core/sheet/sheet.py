from backend.core.accountant.money import Money
from backend.core.order import List
from backend.core.sheet.format import SheetFormat


def _counts(width: int, height: int, item: List, spacing: int) -> tuple[int, int]:
    usable_width = width - 2 * spacing
    usable_height = height - 2 * spacing
    item_width = item.width + 2 * item.bleeds
    item_height = item.height + 2 * item.bleeds

    straight_x = usable_width // item_width
    straight_y = usable_height // item_height
    turned_x = usable_width // item_height
    turned_y = usable_height // item_width

    if straight_x * straight_y > turned_x * turned_y:
        return straight_x, straight_y
    return turned_x, turned_y


class Sheet:
    id: int | None
    version: int
    format: SheetFormat
    density: int
    cost: Money

    def __init__(self, format: SheetFormat, density: int, cost: Money) -> None:
        """Creates a sheet that is not stored yet.

        :param format:
        :param density:
        :param cost: a non-negative rate. Money rejects a negative rate
        before this value can be assigned.

        :return: id is None and version is 0.
        """
        self.id = None
        self.version = 0
        self.format = format
        self.density = density
        self.cost = cost

    def reprice(self, density: int, cost: Money) -> None:
        """Changes the density and the paper rate.

        :param density:
        :param cost: a non-negative rate. Money rejects a negative rate
        before this value can be assigned.

        :return: returns nothing. format, id, and version stay as they were.
        """
        self.cost = cost
        self.density = density

    def item_count(self, item: List, spacing: int) -> int:
        """Counts how many items fit on this sheet.

        :param item: the item cell side is not zero.
        The cell side is the item side plus two bleeds.
        :param spacing: subtracted twice from each side of the sheet.

        :raises ZeroDivisionError: if a side of the item cell is zero.

        :return: the number of items in the layout that fits more.
        When both layouts fit the same number, the turned layout is used.
        Zero items is returned as 0.
        """
        count_x, count_y = _counts(
            self.format.width, self.format.height, item, spacing
        )
        return count_x * count_y

    def cut_needed(self, item: List, spacing: int) -> int:
        """Counts the cuts for the same layout as item_count.

        :param item: the item cell side is not zero.
        The cell side is the item side plus two bleeds.
        :param spacing: subtracted twice from each side of the sheet.

        :raises ZeroDivisionError: if a side of the item cell is zero.

        :return: (max(0, count_x - 1) + max(0, count_y - 1)) * 2 + 4
        for the layout item_count keeps.
        """
        count_x, count_y = _counts(
            self.format.width, self.format.height, item, spacing
        )
        return (max(0, count_x - 1) + max(0, count_y - 1)) * 2 + 4

    def area(self) -> int:
        """Calculates the area of the sheet in square millimeters.

        :return: width * height
        """
        return self.format.width * self.format.height

    def mass(self) -> float:
        """Calculates the mass of the sheet in kilograms.

        :return: area_m2 * (density / 1000)
        """
        area_m2 = self.area() / 1_000_000
        return area_m2 * (self.density / 1000)