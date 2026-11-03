from dataclasses import dataclass


@dataclass(frozen=True)
class SheetFormat:
    name: str
    height: int
    width: int


def standard_formats() -> tuple[SheetFormat, ...]:
    """Returns the six factory formats.

    :return: А1 through А6, in that order. Height is the short side
    and width is the long side. The names use the Russian letter А.
    This function takes no repository and inserts no catalog row.
    """
    return (
        SheetFormat("А1", 594, 841),
        SheetFormat("А2", 420, 594),
        SheetFormat("А3", 297, 420),
        SheetFormat("А4", 210, 297),
        SheetFormat("А5", 148, 210),
        SheetFormat("А6", 105, 148),
    )
