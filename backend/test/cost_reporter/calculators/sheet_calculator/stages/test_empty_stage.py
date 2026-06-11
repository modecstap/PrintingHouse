from decimal import Decimal

import pytest

from backend.cost_reporter.calculators.sheet_calculator.stages.empty_stage import (
    EmptyStage,
)


@pytest.mark.parametrize("call_count", [1, 5, 100])
def test_get_cost_returns_zero(call_count):
    stage = EmptyStage()
    
    for _ in range(call_count):
        assert stage.get_cost() == Decimal(0)


@pytest.mark.parametrize("call_count", [1, 5, 100])
def test_get_cost_price_returns_zero(call_count):
    stage = EmptyStage()
    
    for _ in range(call_count):
        assert stage.get_cost_price() == Decimal(0)


def test_get_cost_and_get_cost_price_return_same_value():
    stage = EmptyStage()
    
    assert stage.get_cost() == stage.get_cost_price()


def test_stage_can_be_instantiated_multiple_times():
    stages = [EmptyStage() for _ in range(3)]
    
    assert all(stage.get_cost() == Decimal(0) for stage in stages)
    assert all(stage.get_cost_price() == Decimal(0) for stage in stages)
