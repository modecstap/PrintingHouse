"""Human-readable paper grade or brand name."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput


@dataclass(frozen=True, slots=True)
class PaperType:
    """
    Value Object. The type or grade of paper (for example offset or coated).
    """

    value: str

    def __post_init__(self) -> None:
        stripped = self.value.strip()
        if not stripped:
            raise InvalidInput(
                subject="PaperType",
                reason="тип бумаги не задан",
            )
        if stripped != self.value:
            object.__setattr__(self, "value", stripped)
