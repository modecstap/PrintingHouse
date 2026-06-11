from decimal import Decimal
from unittest.mock import Mock

import pytest

from backend.cost_reporter.calculators.sheet_calculator.stages.lamination_stage import (
    LaminationStage,
)
from backend.models import Lamination


BASE_COST = Decimal("100")
BASE_COST_PRICE = Decimal("50")
SHEET_LAMINATION_COST = Decimal("10")
INITIAL_PRICE_TOTAL = Decimal("200")


@pytest.fixture
def previous_stage() -> Mock:
    stage = Mock()
    stage.get_cost.return_value = BASE_COST
    stage.get_cost_price.return_value = BASE_COST_PRICE
    return stage


def create_stage(
    previous_stage: Mock,
    lamination: Lamination,
    sheet_lamination_cost: Decimal = SHEET_LAMINATION_COST,
    sheet_count: int = 100,
) -> LaminationStage:
    return LaminationStage(
        previous_stage=previous_stage,
        lamination=lamination,
        sheet_lamination_cost=sheet_lamination_cost,
        sheet_count=sheet_count,
    )


@pytest.mark.parametrize(
    ("lamination", "expected_lamination_cost"),
    [
        (Lamination.DONT, Decimal("0")),
        (Lamination.ONE_ZERO, Decimal("10")),
        (Lamination.ONE_ONE, Decimal("20")),
    ],
)
def test_get_cost_includes_lamination_cost(
    previous_stage: Mock,
    lamination: Lamination,
    expected_lamination_cost: Decimal,
):
    sheet_count = 100
    initial_price = INITIAL_PRICE_TOTAL / sheet_count

    stage = create_stage(
        previous_stage=previous_stage,
        lamination=lamination,
        sheet_count=sheet_count,
    )

    expected_cost = (
        BASE_COST
        + expected_lamination_cost
        + initial_price
    )

    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    ("lamination", "expected_lamination_cost"),
    [
        (Lamination.DONT, Decimal("0")),
        (Lamination.ONE_ZERO, Decimal("10")),
        (Lamination.ONE_ONE, Decimal("20")),
    ],
)
def test_get_cost_price_includes_half_of_lamination_cost(
    previous_stage: Mock,
    lamination: Lamination,
    expected_lamination_cost: Decimal,
):
    sheet_count = 100
    initial_price = INITIAL_PRICE_TOTAL / sheet_count

    stage = create_stage(
        previous_stage=previous_stage,
        lamination=lamination,
        sheet_count=sheet_count,
    )

    expected_cost_price = (
        BASE_COST_PRICE
        + expected_lamination_cost / 2
        + initial_price
    )

    assert stage.get_cost_price() == expected_cost_price


@pytest.mark.parametrize(
    ("sheet_count", "expected_initial_price"),
    [
        (1, Decimal("200")),
        (10, Decimal("20")),
        (200, Decimal("1")),
    ],
)
def test_initial_price_depends_on_sheet_count(
    previous_stage: Mock,
    sheet_count: int,
    expected_initial_price: Decimal,
):
    stage = create_stage(
        previous_stage=previous_stage,
        lamination=Lamination.DONT,
        sheet_count=sheet_count,
    )

    assert stage.get_cost() == BASE_COST + expected_initial_price
