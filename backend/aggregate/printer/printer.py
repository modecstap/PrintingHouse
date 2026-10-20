from backend.aggregate.printer.errors import (
    InsufficientInkException,
    InvalidPriceException,
    InvalidSheetCountException,
)
from backend.aggregate.printer.events import Filled, Printed
from backend.aggregate.printer.money import Money
from backend.aggregate.printer.printing import Printing
from backend.aggregate.printer.values.chroma import Chroma
from backend.aggregate.printer.values.colors import Color
from backend.aggregate.printer.values.ink import Ink
from backend.aggregate.printer.values.printer_id import PrinterID
from backend.aggregate.printer.values.printing_id import PrintingID


def _require_positive_sheet_count(operation: str, sheet_count: object) -> None:
    if type(sheet_count) is not int or sheet_count < 1:
        raise InvalidSheetCountException(
            f"{operation}: число листов {sheet_count!r} должно быть целым не меньше 1"
        )


class Printer:
    def __init__(
            self,
            printer_id: PrinterID,
            cyan: Ink,
            magenta: Ink,
            yellow: Ink,
            black: Ink,
    ) -> None:
        """Принимает номер и четыре стартовых картриджа.

        Побочные эффекты: история и список ожидающих событий пусты.
        Следующий номер записи истории равен 1.
        """
        self.id = printer_id
        self.cyan = cyan
        self.magenta = magenta
        self.yellow = yellow
        self.black = black

        self.printings: list[Printing] = []
        self._next_printing_id = 1
        
        self.pending_events: list[Printed | Filled] = []

    def print(self, chroma: Chroma, sheet_count: int) -> None:
        """Списывает тонер по цветности и записывает печать.

        Предусловия: число листов — int не меньше 1. Остаток каждого
        списываемого цвета не меньше списания.
        Побочные эффекты: уменьшает остатки, дописывает одну запись
        истории и одно ожидающее Printed. Цена картриджа не меняется.
        Ошибки: InvalidSheetCountException, если число листов не int
        или меньше 1. InsufficientInkException, если тонера не хватает.
        При ошибке остатки, история, номер записи и ожидающие события
        не меняются.
        """
        _require_positive_sheet_count("печать", sheet_count)
        cyan_used, magenta_used, yellow_used, black_used = chroma.consumed_sheets(
            sheet_count,
        )
        if (
                self.cyan.sheet_remains < cyan_used
                or self.magenta.sheet_remains < magenta_used
                or self.yellow.sheet_remains < yellow_used
                or self.black.sheet_remains < black_used
        ):
            raise InsufficientInkException(
                "печать: не хватает тонера, "
                f"остатки cyan={self.cyan.sheet_remains}, "
                f"magenta={self.magenta.sheet_remains}, "
                f"yellow={self.yellow.sheet_remains}, "
                f"black={self.black.sheet_remains}, "
                f"списание cyan={cyan_used}, "
                f"magenta={magenta_used}, "
                f"yellow={yellow_used}, "
                f"black={black_used}"
            )
        cyan = Ink(self.cyan.sheet_remains - cyan_used, self.cyan.price)
        magenta = Ink(self.magenta.sheet_remains - magenta_used, self.magenta.price)
        yellow = Ink(self.yellow.sheet_remains - yellow_used, self.yellow.price)
        black = Ink(self.black.sheet_remains - black_used, self.black.price)
        printing = Printing(
            PrintingID(self._next_printing_id),
            chroma,
            sheet_count,
            cyan_used,
            magenta_used,
            yellow_used,
            black_used,
        )
        printed = Printed(
            chroma,
            sheet_count,
            cyan_used,
            magenta_used,
            yellow_used,
            black_used,
        )
        self.cyan = cyan
        self.magenta = magenta
        self.yellow = yellow
        self.black = black
        self.printings.append(printing)
        self.pending_events.append(printed)
        self._next_printing_id += 1

    def fill(self, color: Color, sheet_count: int, price: Money) -> None:
        """Заменяет картридж одного цвета.

        Предусловия: число листов — int не меньше 1. Цена — Money
        со суммой больше нуля.
        Побочные эффекты: заменяет остаток и цену выбранного цвета
        и дописывает одно ожидающее Filled. Историю печати не пишет.
        Ошибки: InvalidSheetCountException, если число листов не int
        или меньше 1. InvalidPriceException, если цена не Money
        или сумма не больше нуля. При ошибке состояние не меняется.
        """
        _require_positive_sheet_count("заправка", sheet_count)
        if not isinstance(price, Money) or price.amount <= 0:
            raise InvalidPriceException(
                f"заправка: цена {price!r} должна быть Money со суммой больше нуля"
            )
        ink = Ink(sheet_count, price)
        filled = Filled(color, sheet_count, price)
        if color is Color.CYAN:
            self.cyan = ink
        elif color is Color.MAGENTA:
            self.magenta = ink
        elif color is Color.YELLOW:
            self.yellow = ink
        elif color is Color.BLACK:
            self.black = ink
        else:
            raise ValueError(f"заправка: неизвестный цвет {color!r}")
        self.pending_events.append(filled)

    def pull_events(self) -> list[Printed | Filled]:
        """Возвращает ожидающие события и очищает их список.

        Результат: события, накопленные с прошлого вызова. Повторный
        вызов возвращает пустой список.
        Побочные эффекты: записывает в pending_events новый пустой
        список. История и остатки не меняются.
        """
        events = self.pending_events
        self.pending_events = []
        return events
