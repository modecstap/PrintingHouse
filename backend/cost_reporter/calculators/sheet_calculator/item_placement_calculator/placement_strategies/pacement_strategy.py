from abc import ABC, abstractmethod

from backend.cost_reporter.models.list_size import ListSize
from backend.cost_reporter.models.press_sheet import PressSheet


class PlacementStrategy(ABC):
    """
    Абстрактная стратегия размещения изделий на листе.
    Использует шаблонный метод для расчета количества изделий и резов.
    """

    def __init__(self, press_sheet: PressSheet, list_size: ListSize):
        self.press_sheet = press_sheet
        self.list_size = list_size

        self.usable_width = self.press_sheet.width - 2 * self.press_sheet.spacing
        self.usable_height = self.press_sheet.height - 2 * self.press_sheet.spacing

        self.item_width = self.list_size.width + 2 * self.list_size.bleeds
        self.item_height = self.list_size.height + 2 * self.list_size.bleeds

        self.count_x = 0
        self.count_y = 0
        self._calculate_counts()

    @abstractmethod
    def _calculate_counts(self):
        """
        Шаблонный метод определяет, как считать count_x и count_y.
        count_x = количество изделий по горизонтали
        count_y = количество изделий по вертикали
        """
        pass

    def get_items_count(self) -> int:
        return int(self.count_x * self.count_y)

    def get_cut_count(self) -> int:
        return max(0, self.count_x - 1) + max(0, self.count_y - 1)
