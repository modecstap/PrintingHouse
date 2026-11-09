from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.format import Format
from backend.new_core.materials.sheet import Sheet


@dataclass(frozen=True, slots=True)
class Imposition:
    """
    Value Object. How target sheets sit on a press sheet, including bleeds and spacing.
    """

    target: Format
    press_sheet: Sheet
    bleeds: int
    spacing: int

    def __post_init__(self) -> None:
        """Rejects a negative bleed or spacing, or a layout that does not fit.

        :raises InvalidInput: if bleeds is below zero, if spacing is
        below zero, if a cell side is zero, or if the grid fits no
        positive number of target sheets. Negative bleeds or spacing are
        reported first without a fit reason in the same error.

        :return: nothing. A bleed or spacing of zero stays.
        """
        reasons: list[str] = []
        if self.bleeds < 0:
            reasons.append(
                f"вылеты меньше 0, вылеты={self.bleeds} мм",
            )
        if self.spacing < 0:
            reasons.append(
                f"поля меньше 0, поля={self.spacing} мм",
            )
        if reasons:
            raise InvalidInput(
                subject="Imposition",
                reason=reasons,
            )
        count_x, count_y = self._axis_counts()
        item_count = count_x * count_y
        if item_count <= 0:
            raise InvalidInput(
                subject="Imposition",
                reason=f"на печатный лист влезает {item_count} целевых листов",
            )

    def thickness(self) -> int:
        return self.press_sheet.thickness()

    def count(self) -> int:
        """Returns how many target sheets fit on the press sheet.

        :return: the product of the chosen grid axes. The straight grid
        is kept only when it fits strictly more sheets than the turned grid.
        """
        count_x, count_y = self._axis_counts()
        return count_x * count_y

    def cuts(self) -> int:
        """Returns the cut count for the same grid as count.

        :return: (max(0, x - 1) + max(0, y - 1)) * 2 + 4
        for the axes count keeps.
        """
        count_x, count_y = self._axis_counts()
        return (max(0, count_x - 1) + max(0, count_y - 1)) * 2 + 4

    def _axis_counts(self) -> tuple[int, int]:
        cell_width = self.target.width + 2 * self.bleeds
        cell_height = self.target.height + 2 * self.bleeds
        if cell_width == 0 or cell_height == 0:
            raise InvalidInput(
                subject="Imposition",
                reason=(
                    "сторона ячейки равна 0, "
                    f"ширина ячейки={cell_width} мм, высота ячейки={cell_height} мм"
                ),
            )

        usable_width = self.press_sheet.format.width - 2 * self.spacing
        usable_height = self.press_sheet.format.height - 2 * self.spacing
        straight_x = usable_width // cell_width
        straight_y = usable_height // cell_height
        turned_x = usable_width // cell_height
        turned_y = usable_height // cell_width
        if straight_x * straight_y > turned_x * turned_y:
            return straight_x, straight_y
        return turned_x, turned_y
