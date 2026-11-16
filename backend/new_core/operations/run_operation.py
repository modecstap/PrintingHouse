from typing import Protocol


__all__ = ["RunOperation"]

class RunOperation(Protocol):  # pylint: disable=too-few-public-methods
    """Marker protocol; each operation is its own type."""
