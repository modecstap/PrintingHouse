"""Code for new_core.print_run.imposition.py.
"""

from dataclasses import dataclass
from decimal import Decimal

from backend.new_core.edges import Edges
from backend.new_core.errors import InvalidInput
from backend.new_core.format import Format
from backend.new_core.materials.sheet import Sheet


__all__ = ["Imposition"]

@dataclass(frozen=True, slots=True)
class Imposition:
    """Value Object. How target sheets sit on a press sheet,
    including bleeds and spacing.
    """

    target: Format
    press_sheet: Sheet
    edges: Edges

    def __post_init__(self) -> None:
        """Rejects a layout that does not fit.

        :raises InvalidInput: if the grid fits no positive number of target
        sheets.
        """
        count_x, count_y = self._axis_counts()
        item_count = count_x * count_y
        if item_count <= 0:
            raise InvalidInput(
                subject="Imposition",
                reason=f"на печатный лист влезает {item_count} целевых листов",
            )

    @property
    def bleeds(self) -> int:
        """Bleeds used for layout, in millimeters."""
        return self.edges.bleeds

    @property
    def spacing(self) -> int:
        """Press-sheet margin used for layout, in millimeters."""
        return self.edges.spacing

    def thickness(self) -> Decimal:
        """Handles thickness.

        :return: the Decimal result.
        """
        return self.press_sheet.thickness()

    def count(self) -> int:
        """Returns how many target sheets fit on the press sheet.

        :return: the int result.
        """
        count_x, count_y = self._axis_counts()
        return count_x * count_y

    def cuts(self) -> int:
        """Returns the cut count for the same grid as count.

        :return: the int result.
        """
        count_x, count_y = self._axis_counts()
        return (max(0, count_x - 1) + max(0, count_y - 1)) * 2 + 4

    def _axis_counts(self) -> tuple[int, int]:
        """Handles axis counts.

        :return: the tuple[int, int] result.
        """
        cell_width = self.target.width + 2 * self.edges.bleeds
        cell_height = self.target.height + 2 * self.edges.bleeds

        usable_width = self.press_sheet.format.width - 2 * self.edges.spacing
        usable_height = self.press_sheet.format.height - 2 * self.edges.spacing
        straight_x = usable_width // cell_width
        straight_y = usable_height // cell_height
        turned_x = usable_width // cell_height
        turned_y = usable_height // cell_width

        if straight_x * straight_y > turned_x * turned_y:
            return straight_x, straight_y
        return turned_x, turned_y
