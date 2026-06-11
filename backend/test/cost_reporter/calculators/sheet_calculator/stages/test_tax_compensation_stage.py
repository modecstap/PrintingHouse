from decimal import Decimal
from unittest.mock import Mock

import pytest

from backend.cost_reporter.calculators.sheet_calculator.stages.tax_compensation_stage import (
    TaxCompensationStage,
)


@pytest.fixture
def previous_stage():
    return Mock()


@pytest.mark.parametrize(
    (
        "previous_cost",
        "previous_cost_price",
        "tax_rate",
        "expected_cost",
    ),
    [
        (
            Decimal("100"),
            Decimal("50"),
            Decimal("1"),
            Decimal("100"),
        ),
        (
            Decimal("100"),
            Decimal("50"),
            Decimal("0.8"),
            Decimal("125"),
        ),
        (
            Decimal("200"),
            Decimal("100"),
            Decimal("0.5"),
            Decimal("400"),
        ),
        (
            Decimal("50"),
            Decimal("30"),
            Decimal("0.9"),
            Decimal("55.55555555555555555555555556"),
        ),
        (
            Decimal("1000"),
            Decimal("600"),
            Decimal("0.75"),
            Decimal("1333.333333333333333333333333"),
        ),
    ],
)
def test_get_cost_divides_by_tax_rate(
    previous_stage,
    previous_cost,
    previous_cost_price,
    tax_rate,
    expected_cost,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = previous_cost_price

    stage = TaxCompensationStage(
        previous_stage=previous_stage,
        tax_rate=tax_rate,
    )

    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    (
        "previous_cost",
        "previous_cost_price",
        "tax_rate",
    ),
    [
        (
            Decimal("100"),
            Decimal("50"),
            Decimal("1"),
        ),
        (
            Decimal("200"),
            Decimal("75"),
            Decimal("0.8"),
        ),
        (
            Decimal("500"),
            Decimal("200"),
            Decimal("0.5"),
        ),
    ],
)
def test_get_cost_price_returns_previous_cost_price_unchanged(
    previous_stage,
    previous_cost,
    previous_cost_price,
    tax_rate,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = previous_cost_price

    stage = TaxCompensationStage(
        previous_stage=previous_stage,
        tax_rate=tax_rate,
    )

    assert stage.get_cost_price() == previous_cost_price


@pytest.mark.parametrize(
    (
        "previous_cost",
        "tax_rate",
    ),
    [
        (
            Decimal("100"),
            Decimal("1"),
        ),
        (
            Decimal("200"),
            Decimal("0.8"),
        ),
        (
            Decimal("300"),
            Decimal("0.5"),
        ),
    ],
)
def test_get_cost_equals_previous_cost_when_tax_rate_is_one(
    previous_stage,
    previous_cost,
    tax_rate,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = Decimal("0")

    stage = TaxCompensationStage(
        previous_stage=previous_stage,
        tax_rate=tax_rate,
    )

    if tax_rate == 1:
        assert stage.get_cost() == previous_cost


@pytest.mark.parametrize(
    (
        "previous_cost",
        "previous_cost_price",
        "tax_rate",
    ),
    [
        (
            Decimal("100"),
            Decimal("50"),
            Decimal("0.8"),
        ),
        (
            Decimal("500"),
            Decimal("300"),
            Decimal("0.75"),
        ),
        (
            Decimal("1000"),
            Decimal("600"),
            Decimal("0.5"),
        ),
    ],
)
def test_previous_stage_methods_called_once_during_initialization(
    previous_stage,
    previous_cost,
    previous_cost_price,
    tax_rate,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = previous_cost_price

    TaxCompensationStage(
        previous_stage=previous_stage,
        tax_rate=tax_rate,
    )

    previous_stage.get_cost.assert_called_once_with()
    previous_stage.get_cost_price.assert_called_once_with()


@pytest.mark.parametrize(
    (
        "previous_cost",
        "tax_rate",
        "expected_result",
    ),
    [
        (
            Decimal("100"),
            Decimal("0.8"),
            Decimal("125"),
        ),
        (
            Decimal("80"),
            Decimal("0.8"),
            Decimal("100"),
        ),
        (
            Decimal("200"),
            Decimal("0.5"),
            Decimal("400"),
        ),
    ],
)
def test_tax_compensation_formula_is_correct(
    previous_stage,
    previous_cost,
    tax_rate,
    expected_result,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = Decimal("0")

    stage = TaxCompensationStage(
        previous_stage=previous_stage,
        tax_rate=tax_rate,
    )

    assert stage.get_cost() == expected_result


@pytest.mark.parametrize(
    (
        "previous_cost",
        "tax_rate",
    ),
    [
        (
            Decimal("100"),
            Decimal("0.8"),
        ),
        (
            Decimal("500"),
            Decimal("0.5"),
        ),
        (
            Decimal("1000"),
            Decimal("0.75"),
        ),
    ],
)
def test_get_cost_not_equal_to_previous_cost_when_tax_rate_less_than_one(
    previous_stage,
    previous_cost,
    tax_rate,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = Decimal("0")

    stage = TaxCompensationStage(
        previous_stage=previous_stage,
        tax_rate=tax_rate,
    )

    if tax_rate < 1:
        assert stage.get_cost() != previous_cost
        assert stage.get_cost() > previous_cost


@pytest.mark.parametrize(
    (
        "previous_cost",
        "previous_cost_price",
        "tax_rate",
    ),
    [
        (
            Decimal("100"),
            Decimal("50"),
            Decimal("0.8"),
        ),
        (
            Decimal("999.99"),
            Decimal("555.55"),
            Decimal("0.95"),
        ),
        (
            Decimal("1"),
            Decimal("1"),
            Decimal("0.25"),
        ),
    ],
)
def test_get_cost_and_get_cost_price_called_multiple_times(
    previous_stage,
    previous_cost,
    previous_cost_price,
    tax_rate,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = previous_cost_price

    stage = TaxCompensationStage(
        previous_stage=previous_stage,
        tax_rate=tax_rate,
    )

    cost1 = stage.get_cost()
    cost2 = stage.get_cost()
    price1 = stage.get_cost_price()
    price2 = stage.get_cost_price()

    assert cost1 == cost2
    assert price1 == price2
    assert previous_stage.get_cost.call_count == 1
    assert previous_stage.get_cost_price.call_count == 1
