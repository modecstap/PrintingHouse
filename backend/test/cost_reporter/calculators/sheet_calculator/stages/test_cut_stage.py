from decimal import Decimal
from unittest.mock import Mock

import pytest

from backend.cost_reporter.calculators.sheet_calculator.stages.cut_stage import (
    CutStage,
)


@pytest.fixture
def previous_stage():
    stage = Mock()
    stage.get_cost.return_value = Decimal("100")
    stage.get_cost_price.return_value = Decimal("80")
    return stage


@pytest.mark.parametrize(
    (
        "cut_cost",
        "cut_count",
        "sheet_count",
        "sheet_in_stack",
        "expected_cost",
    ),
    [
        (
            Decimal("10"),
            1,
            100,
            100,
            Decimal("100.1"),
        ),
        (
            Decimal("10"),
            2,
            101,
            100,
            Decimal("100.3960396039603960396039604"),
        ),
        (
            Decimal("5"),
            3,
            50,
            20,
            Decimal("100.9"),
        ),
    ],
)
def test_get_cost_returns_previous_cost_with_cutting_price(
    previous_stage,
    cut_cost,
    cut_count,
    sheet_count,
    sheet_in_stack,
    expected_cost,
):
    stage = CutStage(
        previous_stage=previous_stage,
        cut_cost=cut_cost,
        cut_count=cut_count,
        sheet_count=sheet_count,
        sheet_in_stack=sheet_in_stack,
    )

    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    (
        "cut_cost",
        "cut_count",
        "sheet_count",
        "sheet_in_stack",
    ),
    [
        (Decimal("10"), 1, 100, 100),
        (Decimal("10"), 2, 101, 100),
        (Decimal("5"), 3, 50, 20),
    ],
)
def test_get_cost_price_returns_previous_cost_price(
    previous_stage,
    cut_cost,
    cut_count,
    sheet_count,
    sheet_in_stack,
):
    stage = CutStage(
        previous_stage=previous_stage,
        cut_cost=cut_cost,
        cut_count=cut_count,
        sheet_count=sheet_count,
        sheet_in_stack=sheet_in_stack,
    )

    assert stage.get_cost_price() == previous_stage.get_cost_price.return_value


@pytest.mark.parametrize(
    (
        "sheet_count",
        "sheet_in_stack",
        "expected_cutting_price",
    ),
    [
        (
            100,
            100,
            Decimal("0.1"),
        ),
        (
            101,
            100,
            Decimal("0.1980198019801980198019801980"),
        ),
        (
            201,
            100,
            Decimal("0.1492537313432835820895522388"),
        ),
    ],
)
def test_cutting_price_uses_ceiling_number_of_stacks(
    previous_stage,
    sheet_count,
    sheet_in_stack,
    expected_cutting_price,
):
    cut_cost = Decimal("10")
    cut_count = 1

    stage = CutStage(
        previous_stage=previous_stage,
        cut_cost=cut_cost,
        cut_count=cut_count,
        sheet_count=sheet_count,
        sheet_in_stack=sheet_in_stack,
    )

    expected_cost = (
        previous_stage.get_cost.return_value + expected_cutting_price
    )

    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    "sheet_count, sheet_in_stack",
    [
        (100, 100),
        (101, 100),
        (50, 20),
    ],
)
def test_previous_stage_methods_are_called_once_during_initialization(
    previous_stage,
    sheet_count,
    sheet_in_stack,
):
    CutStage(
        previous_stage=previous_stage,
        cut_cost=Decimal("10"),
        cut_count=2,
        sheet_count=sheet_count,
        sheet_in_stack=sheet_in_stack,
    )

    previous_stage.get_cost.assert_called_once_with()
    previous_stage.get_cost_price.assert_called_once_with()
