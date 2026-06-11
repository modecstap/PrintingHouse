from decimal import Decimal
from unittest.mock import Mock

import pytest

from backend.cost_reporter.calculators.sheet_calculator.stages.volume_markup_stage import (
    VolumeMarkupStage,
)


PREVIOUS_COST = Decimal("100")
PREVIOUS_COST_PRICE = Decimal("50")


@pytest.fixture
def previous_stage():
    stage = Mock()
    stage.get_cost.return_value = PREVIOUS_COST
    stage.get_cost_price.return_value = PREVIOUS_COST_PRICE
    return stage


@pytest.mark.parametrize(
    (
        "sheet_count",
        "expected_markup",
    ),
    [
        (1, Decimal("1.3")),
        (2, Decimal("1.3")),
        (4, Decimal("1.3")),
    ],
)
def test_get_cost_applies_1_3_markup_for_sheets_less_than_5(
    previous_stage,
    sheet_count,
    expected_markup,
):
    stage = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count,
    )

    expected_cost = PREVIOUS_COST * expected_markup
    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    (
        "sheet_count",
        "expected_markup",
    ),
    [
        (5, Decimal("1.15")),
        (10, Decimal("1.15")),
        (99, Decimal("1.15")),
    ],
)
def test_get_cost_applies_1_15_markup_for_sheets_5_to_99(
    previous_stage,
    sheet_count,
    expected_markup,
):
    stage = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count,
    )

    expected_cost = PREVIOUS_COST * expected_markup
    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    (
        "sheet_count",
        "expected_markup",
    ),
    [
        (100, Decimal("1.05")),
        (250, Decimal("1.05")),
        (499, Decimal("1.05")),
    ],
)
def test_get_cost_applies_1_05_markup_for_sheets_100_to_499(
    previous_stage,
    sheet_count,
    expected_markup,
):
    stage = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count,
    )

    expected_cost = PREVIOUS_COST * expected_markup
    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    (
        "sheet_count",
        "expected_markup",
    ),
    [
        (500, Decimal("1")),
        (1000, Decimal("1")),
        (10000, Decimal("1")),
    ],
)
def test_get_cost_applies_1_0_markup_for_sheets_500_and_more(
    previous_stage,
    sheet_count,
    expected_markup,
):
    stage = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count,
    )

    expected_cost = PREVIOUS_COST * expected_markup
    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    (
        "sheet_count",
    ),
    [
        (1,),
        (50,),
        (250,),
        (1000,),
    ],
)
def test_get_cost_price_returns_previous_cost_price_unchanged(
    previous_stage,
    sheet_count,
):
    stage = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count,
    )

    assert stage.get_cost_price() == PREVIOUS_COST_PRICE


@pytest.mark.parametrize(
    (
        "sheet_count_1",
        "sheet_count_2",
    ),
    [
        (1, 5),
        (99, 100),
        (499, 500),
        (4, 5),
    ],
)
def test_volume_markup_boundaries_are_correct(
    previous_stage,
    sheet_count_1,
    sheet_count_2,
):
    stage1 = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count_1,
    )
    stage2 = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count_2,
    )

    cost1 = stage1.get_cost()
    cost2 = stage2.get_cost()

    if sheet_count_1 < 5 and sheet_count_2 < 5:
        assert cost1 == cost2
    elif sheet_count_1 < 5 and sheet_count_2 >= 5:
        assert cost1 != cost2


@pytest.mark.parametrize(
    (
        "previous_cost",
        "sheet_count",
        "expected_markup",
    ),
    [
        (Decimal("200"), 1, Decimal("1.3")),
        (Decimal("500"), 50, Decimal("1.15")),
        (Decimal("1000"), 200, Decimal("1.05")),
        (Decimal("100"), 1000, Decimal("1")),
    ],
)
def test_volume_markup_calculation_with_different_base_costs(
    previous_stage,
    previous_cost,
    sheet_count,
    expected_markup,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = PREVIOUS_COST_PRICE

    stage = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count,
    )

    expected_cost = previous_cost * expected_markup
    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    (
        "sheet_count",
    ),
    [
        (1,),
        (50,),
        (250,),
        (1000,),
    ],
)
def test_previous_stage_methods_called_once_during_initialization(
    previous_stage,
    sheet_count,
):
    VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count,
    )

    previous_stage.get_cost.assert_called_once_with()
    previous_stage.get_cost_price.assert_called_once_with()


@pytest.mark.parametrize(
    (
        "sheet_count",
    ),
    [
        (1,),
        (50,),
        (250,),
        (1000,),
    ],
)
def test_get_cost_and_get_cost_price_called_multiple_times(
    previous_stage,
    sheet_count,
):
    stage = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count,
    )

    cost1 = stage.get_cost()
    cost2 = stage.get_cost()
    price1 = stage.get_cost_price()
    price2 = stage.get_cost_price()

    assert cost1 == cost2
    assert price1 == price2
    assert previous_stage.get_cost.call_count == 1
    assert previous_stage.get_cost_price.call_count == 1


@pytest.mark.parametrize(
    (
        "sheet_count",
    ),
    [
        (1,),
        (50,),
        (250,),
        (1000,),
    ],
)
def test_get_cost_not_less_than_previous_cost(
    previous_stage,
    sheet_count,
):
    stage = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count,
    )

    assert stage.get_cost() >= PREVIOUS_COST


@pytest.mark.parametrize(
    (
        "sheet_count",
        "max_expected_cost",
    ),
    [
        (1, PREVIOUS_COST * Decimal("1.3")),
        (50, PREVIOUS_COST * Decimal("1.15")),
        (250, PREVIOUS_COST * Decimal("1.05")),
        (1000, PREVIOUS_COST * Decimal("1")),
    ],
)
def test_volume_markup_does_not_exceed_maximum(
    previous_stage,
    sheet_count,
    max_expected_cost,
):
    stage = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count,
    )

    assert stage.get_cost() <= max_expected_cost


@pytest.mark.parametrize(
    (
        "previous_cost",
        "previous_cost_price",
        "sheet_count",
    ),
    [
        (Decimal("100"), Decimal("50"), 1),
        (Decimal("500"), Decimal("250"), 50),
        (Decimal("1000"), Decimal("600"), 250),
        (Decimal("200"), Decimal("100"), 1000),
    ],
)
def test_get_cost_differs_from_get_cost_price_when_previous_differs(
    previous_stage,
    previous_cost,
    previous_cost_price,
    sheet_count,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = previous_cost_price

    stage = VolumeMarkupStage(
        previous_stage=previous_stage,
        sheet_count=sheet_count,
    )

    if previous_cost != previous_cost_price:
        assert stage.get_cost() != stage.get_cost_price()
