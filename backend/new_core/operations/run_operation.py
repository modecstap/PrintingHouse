from typing import Protocol


class RunOperation(Protocol):  # pylint: disable=too-few-public-methods
    """Marker protocol; each operation is its own type."""
