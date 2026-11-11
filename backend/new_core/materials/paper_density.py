"""Paper grammage in grams per square meter."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput


@dataclass(frozen=True, slots=True)
class PaperDensity:
    """
    Value Object. Paper density in grams per square meter (г/м²).
    """

    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise InvalidInput(
                subject="PaperDensity",
                reason=(
                    f"плотность бумаги меньше или равна 0, "
                    f"плотность={self.value} г/м²"
                ),
            )
