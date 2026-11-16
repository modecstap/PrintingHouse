"""PaperDensity value object validation."""

import re

import pytest

from backend.new_core.errors import InvalidInput
from backend.new_core.materials.paper_density import PaperDensity


__all__ = [
    "test_paper_density_rejects_non_positive",
    "test_paper_density_keeps_positive_value",
]

def _rejects(message: str, call: object) -> None:
    """Handles rejects.

    :param message: the message.
    :param call: the call.
    """
    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        call()


@pytest.mark.parametrize("value", [0, -1])
def test_paper_density_rejects_non_positive(value: int) -> None:
    """Non-positive density is rejected with grammage units in the message.

    :param value: the value.
    """
    _rejects(
        (
            f"PaperDensity: плотность бумаги меньше или равна 0, "
            f"плотность={value} г/м²"
        ),
        lambda: PaperDensity(value),
    )


def test_paper_density_keeps_positive_value() -> None:
    """A positive density keeps its numeric value."""
    density = PaperDensity(80)
    assert density.value == 80
