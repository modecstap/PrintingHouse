"""Target size in millimeters."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput


@dataclass(frozen=True, slots=True)
class Format:
    """
    Value Object. The name and the height and width of a target, in millimeters.
    """

    name: str
    height: int
    width: int

    def __post_init__(self) -> None:
        """Rejects a negative side.

        :raises InvalidInput: if height is below zero, or if width is
        below zero. Both failures are reported together.

        :return: nothing. A side of zero stays.
        """
        reasons: list[str] = []
        if self.height < 0:
            reasons.append(
                f"высота меньше 0, высота={self.height} мм",
            )
        if self.width < 0:
            reasons.append(
                f"ширина меньше 0, ширина={self.width} мм",
            )
        if reasons:
            raise InvalidInput(
                subject="Format",
                reason=reasons,
            )
