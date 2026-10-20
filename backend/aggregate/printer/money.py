from decimal import Decimal

from backend.aggregate.printer.errors import InvalidPriceException


class Money:
    def __init__(self, amount: Decimal) -> None:
        """Сохраняет неотрицательную сумму.

        Предусловия: amount имеет тип Decimal и не меньше нуля.
        Результат: объект с полем amount, равным переданному Decimal.
        Ошибки: InvalidPriceException, если тип не Decimal или сумма меньше нуля.
        """
        if type(amount) is not Decimal or amount < 0:
            raise InvalidPriceException(
                f"создание цены: сумма {amount!r} должна быть неотрицательным Decimal"
            )
        self.amount = amount

    def __eq__(self, other: object) -> bool:
        if type(other) is not Money:
            return NotImplemented
        return self.amount == other.amount
