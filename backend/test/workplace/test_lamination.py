import re

import pytest

from backend.workplace.workplaces.lamination.models import Lamination


def test_lamination_values_match_the_saved_names():
    assert (
        Lamination.DONT.value,
        Lamination.ONE_ZERO.value,
        Lamination.ONE_ONE.value,
    ) == (1, 2, 3)


def test_lamination_film_sides_returns_side_count():
    assert Lamination.DONT.film_sides() == 0
    assert Lamination.ONE_ZERO.film_sides() == 1
    assert Lamination.ONE_ONE.film_sides() == 2


def test_lamination_film_sides_rejects_other_member():
    member = object()
    with pytest.raises(
        ValueError,
        match=re.escape(f"число сторон плёнки: {member!r}"),
    ):
        Lamination.film_sides(member)
