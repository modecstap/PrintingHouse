"""PaperDensity value object validation."""

import re

import pytest

from backend.new_core.errors import InvalidInput
from backend.new_core.materials.paper_density import PaperDensity


def _rejects(message: str, call) -> None:
    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        call()


@pytest.mark.parametrize("value", [0, -1])
def test_paper_density_rejects_non_positive(value: int) -> None:
    """Non-positive density is rejected with grammage units in the message."""
    _rejects(
        f"PaperDensity: плотность бумаги меньше или равна 0, плотность={value} г/м²",
        lambda: PaperDensity(value),
    )


def test_paper_density_keeps_positive_value() -> None:
    """A positive density keeps its numeric value."""
    density = PaperDensity(80)
    assert density.value == 80
