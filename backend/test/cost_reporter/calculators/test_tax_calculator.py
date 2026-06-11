from decimal import Decimal

import pytest

from backend.cost_reporter.calculators.tax_calculator import TaxCalculator


@pytest.mark.parametrize(
    "tax_rate, profit_before_tax, expected_profit_after_tax",
    [
        (
            Decimal("0"),
            Decimal("100"),
            Decimal("0"),
        ),
        (
            Decimal("1"),
            Decimal("100"),
            Decimal("100"),
        ),
        (
            Decimal("0.2"),
            Decimal("123.45"),
            Decimal("24.690"),
        ),
    ],
)
def test_profit_after_tax_returns_calculated_value(
    tax_rate: Decimal,
    profit_before_tax: Decimal,
    expected_profit_after_tax: Decimal,
):
    calculator = TaxCalculator(
        tax_rate=tax_rate,
        profit_before_tax=profit_before_tax,
    )

    assert calculator.profit_after_tax() == expected_profit_after_tax


@pytest.mark.parametrize(
    "tax_rate, profit_before_tax",
    [
        (
            Decimal("0"),
            Decimal("0"),
        ),
        (
            Decimal("0.2"),
            Decimal("100"),
        ),
        (
            Decimal("999.99"),
            Decimal("123456789.123456789"),
        ),
    ],
)
def test_profit_before_tax_returns_original_value(
    tax_rate: Decimal,
    profit_before_tax: Decimal,
):
    calculator = TaxCalculator(
        tax_rate=tax_rate,
        profit_before_tax=profit_before_tax,
    )

    assert calculator.profit_before_tax() == profit_before_tax
