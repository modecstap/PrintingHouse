from decimal import Decimal
from unittest.mock import Mock

import pytest

from backend.cost_reporter.calculators.sheet_calculator.stages.print_stage import (
    PrintStage,
)
from backend.models import Chroma


@pytest.fixture
def previous_stage():
    stage = Mock()
    stage.get_cost.return_value = Decimal("100")
    stage.get_cost_price.return_value = Decimal("80")
    return stage


@pytest.fixture
def ink_prices():
    return {
        "color": Decimal("15"),
        "black": Decimal("5"),
    }


@pytest.mark.parametrize(
    (
        "chroma",
        "salary",
        "expected_cost",
    ),
    [
        (
            Chroma.ZERO_ZERO,
            Decimal("10"),
            Decimal("100"),
        ),
        (
            Chroma.ONE_ZERO,
            Decimal("10"),
            Decimal("115"),
        ),
        (
            Chroma.FOUR_FOUR,
            Decimal("10"),
            Decimal("140"),
        ),
    ],
)
def test_get_cost_returns_previous_cost_with_salary_and_ink_cost(
    previous_stage,
    ink_prices,
    chroma,
    salary,
    expected_cost,
):
    stage = PrintStage(
        previous_stage=previous_stage,
        salary_by_sheet=salary,
        color_ink_cost=ink_prices["color"],
        black_ink_cost=ink_prices["black"],
        chroma=chroma,
    )

    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    (
        "chroma",
        "expected_cost_price",
    ),
    [
        (
            Chroma.ZERO_ZERO,
            Decimal("80"),
        ),
        (
            Chroma.ONE_ONE,
            Decimal("90"),
        ),
        (
            Chroma.FOUR_ONE,
            Decimal("100"),
        ),
    ],
)
def test_get_cost_price_returns_previous_cost_price_with_ink_cost(
    previous_stage,
    ink_prices,
    chroma,
    expected_cost_price,
):
    stage = PrintStage(
        previous_stage=previous_stage,
        salary_by_sheet=Decimal("10"),
        color_ink_cost=ink_prices["color"],
        black_ink_cost=ink_prices["black"],
        chroma=chroma,
    )

    assert stage.get_cost_price() == expected_cost_price


@pytest.mark.parametrize(
    (
        "chroma",
        "expected_ink_cost",
    ),
    [
        (
            Chroma.ONE_ZERO,
            Decimal("5"),
        ),
        (
            Chroma.ONE_ONE,
            Decimal("10"),
        ),
        (
            Chroma.FOUR_ZERO,
            Decimal("15"),
        ),
        (
            Chroma.FOUR_ONE,
            Decimal("20"),
        ),
        (
            Chroma.FOUR_FOUR,
            Decimal("30"),
        ),
    ],
)
def test_get_cost_price_contains_correct_ink_cost_for_each_chroma(
    previous_stage,
    ink_prices,
    chroma,
    expected_ink_cost,
):
    base_cost_price = previous_stage.get_cost_price.return_value

    stage = PrintStage(
        previous_stage=previous_stage,
        salary_by_sheet=Decimal("999"),
        color_ink_cost=ink_prices["color"],
        black_ink_cost=ink_prices["black"],
        chroma=chroma,
    )

    assert stage.get_cost_price() == base_cost_price + expected_ink_cost


@pytest.mark.parametrize(
    "chroma",
    [
        Chroma.ZERO_ZERO,
        Chroma.ONE_ZERO,
        Chroma.FOUR_FOUR,
    ],
)
def test_previous_stage_methods_are_called_once_during_initialization(
    previous_stage,
    ink_prices,
    chroma,
):
    PrintStage(
        previous_stage=previous_stage,
        salary_by_sheet=Decimal("10"),
        color_ink_cost=ink_prices["color"],
        black_ink_cost=ink_prices["black"],
        chroma=chroma,
    )

    previous_stage.get_cost.assert_called_once_with()
    previous_stage.get_cost_price.assert_called_once_with()
