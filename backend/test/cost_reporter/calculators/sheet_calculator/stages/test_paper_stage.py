from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from backend.cost_reporter.calculators.sheet_calculator.stages.paper_stage import (
    KILO_COEFFICIENT,
    METRE_COEFFICIENT,
    PaperStage,
)


@pytest.fixture
def previous_stage():
    return Mock()


@pytest.fixture
def press_sheet_factory():
    def _create(width: int, height: int):
        return SimpleNamespace(width=width, height=height)

    return _create


@pytest.mark.parametrize(
    (
        "width",
        "height",
        "paper_cost_per_kg",
        "density",
        "previous_cost",
        "expected_cost",
    ),
    [
        (
            1000,
            1000,
            Decimal("1"),
            1000,
            Decimal("0"),
            Decimal("1"),
        ),
        (
            500,
            200,
            Decimal("2.5"),
            120,
            Decimal("10"),
            Decimal("10.03"),
        ),
        (
            0,
            1000,
            Decimal("100"),
            300,
            Decimal("15"),
            Decimal("15"),
        ),
    ],
)
def test_get_cost_returns_previous_cost_with_paper_cost(
    previous_stage,
    press_sheet_factory,
    width,
    height,
    paper_cost_per_kg,
    density,
    previous_cost,
    expected_cost,
):
    previous_stage.get_cost.return_value = previous_cost
    previous_stage.get_cost_price.return_value = Decimal("0")

    press_sheet = press_sheet_factory(width, height)

    stage = PaperStage(
        previous_stage=previous_stage,
        press_sheet=press_sheet,
        kilograms_paper_cost=paper_cost_per_kg,
        density=density,
    )

    assert stage.get_cost() == expected_cost


@pytest.mark.parametrize(
    (
        "width",
        "height",
        "paper_cost_per_kg",
        "density",
        "previous_cost_price",
        "expected_cost_price",
    ),
    [
        (
            1000,
            1000,
            Decimal("1"),
            1000,
            Decimal("0"),
            Decimal("1"),
        ),
        (
            500,
            200,
            Decimal("2.5"),
            120,
            Decimal("7"),
            Decimal("7.03"),
        ),
        (
            1000,
            1000,
            Decimal("0"),
            300,
            Decimal("11"),
            Decimal("11"),
        ),
    ],
)
def test_get_cost_price_returns_previous_cost_price_with_paper_cost(
    previous_stage,
    press_sheet_factory,
    width,
    height,
    paper_cost_per_kg,
    density,
    previous_cost_price,
    expected_cost_price,
):
    previous_stage.get_cost.return_value = Decimal("0")
    previous_stage.get_cost_price.return_value = previous_cost_price

    press_sheet = press_sheet_factory(width, height)

    stage = PaperStage(
        previous_stage=previous_stage,
        press_sheet=press_sheet,
        kilograms_paper_cost=paper_cost_per_kg,
        density=density,
    )

    assert stage.get_cost_price() == expected_cost_price
