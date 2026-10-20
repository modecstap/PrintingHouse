from decimal import Decimal

from backend.aggregate.printer.errors import InvalidSheetCountException
from backend.aggregate.printer.money import Money


class Ink:
    def __init__(self, sheet_remains: int = 0, price: Money | None = None) -> None:
        """Сохраняет остаток листов и цену картриджа.

        Предусловия: sheet_remains имеет тип int и не меньше 0.
        Если price не передан, цена равна нулю.
        Результат: объект с полями sheet_remains и price.
        Ошибки: InvalidSheetCountException, если число листов не int или меньше 0.
        """
        if type(sheet_remains) is not int or sheet_remains < 0:
            raise InvalidSheetCountException(
                f"создание картриджа: остаток {sheet_remains!r} должен быть целым не меньше 0"
            )
        if price is None:
            price = Money(Decimal("0"))
        self.sheet_remains = sheet_remains
        self.price = price

    def __eq__(self, other: object) -> bool:
        if type(other) is not Ink:
            return NotImplemented
        return (
            self.sheet_remains == other.sheet_remains
            and self.price == other.price
        )
