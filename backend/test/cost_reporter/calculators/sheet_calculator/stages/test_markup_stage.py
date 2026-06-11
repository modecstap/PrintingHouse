from decimal import Decimal
from unittest.mock import Mock

import pytest

from backend.cost_reporter.calculators.sheet_calculator.stages.markup_stage import (
    MarkupStage,
)


@pytest.fixture
def previous_stage():
    return Mock()


@pytest.mark.parametrize(
    (
        "previous_cost",
        "previous_cost_price",
        "markup_percent",
        "expected_cost",
    ),
    [
        (
            Decimal("100"),
            Decimal("50"),
            Decimal("0"),
            Decimal("100"),
        ),
        (
            Decimal("100"),
            Decimal("50"),
            Decimal("50"),
            Decimal("150"),
        ),
        (
            Decimal("200"),
            Decimal("100"),
            Decimal("25"),
            Decimal("250"),
        ),
        (
            Decimal("1000"),
            Decimal("800"),
            Decimal("100"),
            Decimal("2000"),
        ),
        (
            Decimal("50"),
            Decimal("30"),
            Decimal("10"),
            Decimal("55"),
        ),
    ],
)
def test_get_cost_applies_markup_correctly(
    previous_stage,
    previous_cost,
    previous_cost_price,
    markup_percent,
    expected_cost,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = previous_cost_price

    stage = MarkupStage(
        previous_stage=previous_stage,
        markup=markup_percent,
    )

    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    (
        "previous_cost",
        "previous_cost_price",
        "markup_percent",
    ),
    [
        (
            Decimal("100"),
            Decimal("50"),
            Decimal("0"),
        ),
        (
            Decimal("200"),
            Decimal("75"),
            Decimal("50"),
        ),
        (
            Decimal("500"),
            Decimal("200"),
            Decimal("25"),
        ),
    ],
)
def test_get_cost_price_returns_previous_cost_price_unchanged(
    previous_stage,
    previous_cost,
    previous_cost_price,
    markup_percent,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = previous_cost_price

    stage = MarkupStage(
        previous_stage=previous_stage,
        markup=markup_percent,
    )

    assert stage.get_cost_price() == previous_cost_price


@pytest.mark.parametrize(
    (
        "previous_cost",
        "markup_percent",
    ),
    [
        (
            Decimal("100"),
            Decimal("0"),
        ),
        (
            Decimal("200"),
            Decimal("50"),
        ),
        (
            Decimal("300"),
            Decimal("100"),
        ),
    ],
)
def test_get_cost_not_equal_to_previous_cost_when_markup_applied(
    previous_stage,
    previous_cost,
    markup_percent,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = Decimal("0")

    stage = MarkupStage(
        previous_stage=previous_stage,
        markup=markup_percent,
    )

    if markup_percent != 0:
        assert stage.get_cost() != previous_cost


@pytest.mark.parametrize(
    (
        "previous_cost",
        "previous_cost_price",
        "markup_percent",
    ),
    [
        (
            Decimal("100"),
            Decimal("50"),
            Decimal("50"),
        ),
        (
            Decimal("500"),
            Decimal("300"),
            Decimal("25"),
        ),
        (
            Decimal("1000"),
            Decimal("600"),
            Decimal("200"),
        ),
    ],
)
def test_previous_stage_methods_called_once_during_initialization(
    previous_stage,
    previous_cost,
    previous_cost_price,
    markup_percent,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = previous_cost_price

    MarkupStage(
        previous_stage=previous_stage,
        markup=markup_percent,
    )

    previous_stage.get_cost.assert_called_once_with()
    previous_stage.get_cost_price.assert_called_once_with()


@pytest.mark.parametrize(
    (
        "previous_cost",
        "markup_percent",
        "expected_multiplier",
    ),
    [
        (
            Decimal("100"),
            Decimal("10"),
            Decimal("1.1"),
        ),
        (
            Decimal("100"),
            Decimal("50"),
            Decimal("1.5"),
        ),
        (
            Decimal("100"),
            Decimal("200"),
            Decimal("3"),
        ),
    ],
)
def test_markup_formula_is_correct(
    previous_stage,
    previous_cost,
    markup_percent,
    expected_multiplier,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = Decimal("0")

    stage = MarkupStage(
        previous_stage=previous_stage,
        markup=markup_percent,
    )

    expected_cost = previous_cost * expected_multiplier
    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    (
        "previous_cost",
        "previous_cost_price",
        "markup_percent",
    ),
    [
        (
            Decimal("100"),
            Decimal("50"),
            Decimal("0"),
        ),
        (
            Decimal("999.99"),
            Decimal("555.55"),
            Decimal("33.33"),
        ),
        (
            Decimal("1"),
            Decimal("1"),
            Decimal("500"),
        ),
    ],
)
def test_get_cost_and_get_cost_price_called_multiple_times(
    previous_stage,
    previous_cost,
    previous_cost_price,
    markup_percent,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = previous_cost_price

    stage = MarkupStage(
        previous_stage=previous_stage,
        markup=markup_percent,
    )

    cost1 = stage.get_cost()
    cost2 = stage.get_cost()
    price1 = stage.get_cost_price()
    price2 = stage.get_cost_price()

    assert cost1 == cost2
    assert price1 == price2
    assert previous_stage.get_cost.call_count == 1
    assert previous_stage.get_cost_price.call_count == 1
