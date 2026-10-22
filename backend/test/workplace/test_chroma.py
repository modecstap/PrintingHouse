import pytest

from backend.workplace.chroma import Chroma


def test_chroma_values_match_the_saved_names():
    assert (
        Chroma.ZERO_ZERO.value,
        Chroma.ONE_ZERO.value,
        Chroma.ONE_ONE.value,
        Chroma.FOUR_ZERO.value,
        Chroma.FOUR_ONE.value,
        Chroma.FOUR_FOUR.value,
    ) == (0, 1, 2, 3, 4, 5)


@pytest.mark.parametrize(
    ("chroma", "sheets"),
    [
        (Chroma.ZERO_ZERO, (0, 0, 0, 0)),
        (Chroma.ONE_ZERO, (0, 0, 0, 1)),
        (Chroma.ONE_ONE, (0, 0, 0, 2)),
        (Chroma.FOUR_ZERO, (1, 1, 1, 1)),
        (Chroma.FOUR_ONE, (1, 1, 1, 2)),
        (Chroma.FOUR_FOUR, (2, 2, 2, 2)),
    ],
)
def test_chroma_consumed_sheets_uses_member_coefficients(
    chroma: Chroma,
    sheets: tuple[int, int, int, int],
):
    assert chroma.consumed_sheets(1) == sheets


def test_chroma_consumed_sheets_scales_with_sheet_count():
    assert Chroma.FOUR_ONE.consumed_sheets(3) == (3, 3, 3, 6)
