from decimal import Decimal
from unittest.mock import Mock

import pytest

from backend.cost_reporter.calculators.sheet_calculator.stages.die_cutting_stage import (
    DieCuttingStage,
)


@pytest.fixture
def previous_stage():
    return Mock()


@pytest.mark.parametrize(
    ("previous_cost", "die_cutting_cost", "expected_cost"),
    [
        (
            Decimal("100"),
            Decimal("20"),
            Decimal("120"),
        ),
        (
            Decimal("100"),
            Decimal("0"),
            Decimal("100"),
        ),
        (
            Decimal("0"),
            Decimal("20"),
            Decimal("20"),
        ),
    ],
)
def test_get_cost_returns_previous_cost_plus_die_cutting_cost(
    previous_stage,
    previous_cost,
    die_cutting_cost,
    expected_cost,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = Decimal("50")

    stage = DieCuttingStage(
        previous_stage=previous_stage,
        die_cutting_cost=die_cutting_cost,
    )

    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    ("cost_price",),
    [
        (Decimal("0"),),
        (Decimal("15.75"),),
        (Decimal("999999.99"),),
    ],
)
def test_get_cost_price_returns_value_from_previous_stage(
    previous_stage,
    cost_price,
):
    previous_stage.get_cost.return_value = Decimal("100")
    previous_stage.get_cost_price.return_value = cost_price

    stage = DieCuttingStage(
        previous_stage=previous_stage,
        die_cutting_cost=Decimal("20"),
    )

    assert stage.get_cost_price() == cost_price


@pytest.mark.parametrize(
    ("previous_cost", "die_cutting_cost"),
    [
        (
            Decimal("100"),
            Decimal("20"),
        ),
        (
            Decimal("1"),
            Decimal("999"),
        ),
        (
            Decimal("-50"),
            Decimal("25"),
        ),
    ],
)
def test_get_cost_is_not_equal_to_previous_cost_or_die_cutting_cost_alone(
    previous_stage,
    previous_cost,
    die_cutting_cost,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = Decimal("10")

    stage = DieCuttingStage(
        previous_stage=previous_stage,
        die_cutting_cost=die_cutting_cost,
    )

    expected_cost = previous_cost + die_cutting_cost

    assert stage.get_cost() == expected_cost

    if expected_cost != previous_cost:
        assert stage.get_cost() != previous_cost

    if expected_cost != die_cutting_cost:
        assert stage.get_cost() != die_cutting_cost
