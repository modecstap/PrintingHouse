from decimal import ROUND_HALF_UP, Decimal

from backend.new_core.errors import InvalidPriceException


__all__ = ["Money"]

def _decimal_factor(factor: object) -> Decimal | None:
    # bool is a subclass of int; isinstance(True, int) would accept bool.
    if type(factor) in (int, float):  # pylint: disable=unidiomatic-typecheck
        return Decimal(factor)
    if isinstance(factor, Decimal):
        return factor
    return None


class Money:
    amount: Decimal

    def __init__(self, amount: Decimal) -> None:
        """Stores a non-negative amount.

        :param amount: the type is Decimal and the amount is not below zero.

        :raises InvalidPriceException: if the type is not Decimal
        or the amount is below zero.

        :return: an object whose amount is the passed Decimal rounded to cents
        (half up). Addition accepts another Money. Multiplication and division
        accept Decimal or int. Each operation returns a new Money.
        """
        if not isinstance(amount, Decimal) or amount < 0:
            raise InvalidPriceException(
                "создание цены: сумма "
                f"{amount!r} должна быть неотрицательным Decimal"
            )
        self.amount = amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    @classmethod
    def zero(cls) -> "Money":
        return Money(Decimal(0))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
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
