"""Code for new_core.operations.laminate.lamination.py.
"""

from enum import Enum


__all__ = ["Lamination"]

class Lamination(Enum):
    """Lamination.
    """
    DONT = 1
    ONE_ZERO = 2
    ONE_ONE = 3

    def film_sides(self) -> int:
        """Returns the number of film sides.

        :raises ValueError: if there is no lamination.

        :return: the int result.
        """
        if self is Lamination.DONT:
            return 0
        if self is Lamination.ONE_ZERO:
            return 1
        if self is Lamination.ONE_ONE:
            return 2
        raise ValueError(f"число сторон плёнки: {self!r}")
