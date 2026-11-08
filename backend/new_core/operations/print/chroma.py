from enum import Enum


class Chroma(Enum):
    ZERO_ZERO = 0
    ONE_ZERO = 1
    ONE_ONE = 2
    FOUR_ZERO = 3
    FOUR_ONE = 4
    FOUR_FOUR = 5

    def consumed_sheets(self, sheet_count: int) -> tuple[int, int, int, int]:
        """Returns the cyan, magenta, yellow, and black consumption.

        :param sheet_count:

        :return: four integers in the order cyan, magenta, yellow, black.
        """
        cyan_factor, magenta_factor, yellow_factor, black_factor = _FACTORS[self]
        return (
            cyan_factor * sheet_count,
            magenta_factor * sheet_count,
            yellow_factor * sheet_count,
            black_factor * sheet_count,
        )


_FACTORS: dict[Chroma, tuple[int, int, int, int]] = {
    Chroma.ZERO_ZERO: (0, 0, 0, 0),
    Chroma.ONE_ZERO: (0, 0, 0, 1),
    Chroma.ONE_ONE: (0, 0, 0, 2),
    Chroma.FOUR_ZERO: (1, 1, 1, 1),
    Chroma.FOUR_ONE: (1, 1, 1, 2),
    Chroma.FOUR_FOUR: (2, 2, 2, 2),
}
