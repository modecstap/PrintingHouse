"""FilmDensity value object validation."""

import re

import pytest

from backend.new_core.errors import InvalidInput
from backend.new_core.materials.film_density import FilmDensity


def _rejects(message: str, call) -> None:
    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        call()


@pytest.mark.parametrize("value", [0, -1])
def test_film_density_rejects_non_positive(value: int) -> None:
    """Non-positive density is rejected with micron units in the message."""
    _rejects(
        f"FilmDensity: плотность плёнки меньше или равна 0, плотность={value} мкм",
        lambda: FilmDensity(value),
    )


def test_film_density_keeps_positive_value() -> None:
    """A positive density keeps its numeric value."""
    density = FilmDensity(90)
    assert density.value == 90
