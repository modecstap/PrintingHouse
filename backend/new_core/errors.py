"""Domain and validation errors shared across new_core.
"""

from collections.abc import Sequence


__all__ = [
    "InvalidPriceException",
    "InvalidInput",
]

class InvalidPriceException(Exception):
    """Invalid Price Exception.
    """
    pass


class InvalidInput(Exception):
    """Invalid Input.
    """
    def __init__(self, subject: str, reason: str | Sequence[str]) -> None:
        """Stores the rejected data and why it was rejected.

        :param subject: the name of the rejected data.
        :param reason: why that data is rejected. A sequence lists every
        """
        if not isinstance(reason, str):
            reason = "; ".join(reason)
        self.subject = subject
        self.reason = reason
        super().__init__(f"{subject}: {reason}")
