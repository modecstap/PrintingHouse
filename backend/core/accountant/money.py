from decimal import ROUND_HALF_UP, Decimal

from backend.core.errors import InvalidPriceException


def _decimal_factor(factor: object) -> Decimal | None:
    if type(factor) is int or float:
        return Decimal(factor)
    if type(factor) is Decimal:
        return factor
    return None


class Money:
    amount: Decimal

    def __init__(self, amount: Decimal) -> None:
        """Stores a non-negative amount.

        :param amount: the type is Decimal and the amount is not below zero.

        :raises InvalidPriceException: if the type is not Decimal
        or the amount is below zero.

        :return: an object whose amount field equals the passed Decimal.
        Addition accepts another Money. Multiplication and division accept Decimal
        or int. Each operation returns a new Money.
        """
        if type(amount) is not Decimal or amount < 0:
            raise InvalidPriceException(
                f"создание цены: сумма {amount!r} должна быть неотрицательным Decimal"
            )
        self.amount = amount

    @classmethod
    def zero(cls) -> "Money":
        return Money(Decimal(0))

    def __eq__(self, other: object) -> bool:
        if type(other) is not Money:
            return NotImplemented
        return self.amount == other.amount

    def __add__(self, other: object) -> "Money":
        if type(other) is not Money:
            return NotImplemented
        return Money(self.amount + other.amount)

    def __mul__(self, factor: object) -> "Money":
        decimal_factor = _decimal_factor(factor)
        if decimal_factor is None:
            return NotImplemented
        return Money(self.amount * decimal_factor)

    def __truediv__(self, divisor: object) -> "Money":
        decimal_divisor = _decimal_factor(divisor)
        if decimal_divisor is None:
            return NotImplemented
        return Money(self.amount / decimal_divisor)

    def quantize(self) -> "Money":
        rounded = self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Money(rounded)
