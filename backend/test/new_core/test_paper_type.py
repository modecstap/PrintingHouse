"""PaperType value object validation."""

import re

import pytest

from backend.new_core.errors import InvalidInput
from backend.new_core.materials.paper_type import PaperType


def _rejects(message: str, call) -> None:
    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        call()


@pytest.mark.parametrize("raw", ["", "   "])
def test_paper_type_rejects_blank(raw: str) -> None:
    """Empty or whitespace-only type is rejected."""
    _rejects(
        "PaperType: тип бумаги не задан",
        lambda: PaperType(raw),
    )


def test_paper_type_strips_surrounding_whitespace() -> None:
    """Surrounding spaces are removed from the canonical value."""
    paper_type = PaperType("  офсет  ")
    assert paper_type.value == "офсет"
