"""JSON mapping round-trip and validation rules."""

from dataclasses import replace
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.product import Product
from backend.new_core.part import Part
from backend.new_core.personal.die_cutter_operator import DieCutterOperatorID
from backend.new_core.values.money import Money
from backend.server.mapping import (
    order_to_dto,
    product_from_dto,
    product_to_dto,
    reference_from_dto,
    reference_to_dto,
)
from backend.server.schemas import ProductDto, ReferenceDto
from backend.test.new_core.test_print_run import build_worked_run
from backend.test.storage.helpers import product_from_run


def _product_with_die_cut() -> Product:
    run, *_ = build_worked_run(with_cut=False)
    block: Part = replace(
        run.block,
        operations=run.block.operations + (DieCut(operator_id=DieCutterOperatorID(2)),),
    )
    return Product(
        blocks=(block,),
        operations=product_from_run(run).operations,
    )


def test_full_product_all_kinds_round_trip():
    product = _product_with_die_cut()
    dto = product_to_dto(product)
    restored = product_from_dto(dto)
    assert restored == product


def test_money_json_number_rejected():
    product = product_from_run(build_worked_run()[0])
    dto = product_to_dto(product)
    dumped = dto.model_dump()
    dumped["blocks"][0]["imposition"]["press_sheet"]["paper"]["price_per_kilo"] = 1
    with pytest.raises(ValidationError):
        ProductDto.model_validate(dumped)


def test_unknown_kind_rejected():
    payload = {
        "blocks": [
            {
                "imposition": {
                    "target": {"name": "t", "height": 10, "width": 10},
                    "press_sheet": {
                        "paper": {
                            "density": 100,
                            "thickness": 1,
                            "name": "p",
                            "price_per_kilo": "1",
                        },
                        "format": {"name": "f", "height": 100, "width": 200},
                    },
                    "bleeds": 0,
                    "spacing": 0,
                },
                "count": 1,
                "markup": 0,
                "operations": [{"kind": "unknown", "operator_id": 1}],
            }
        ],
        "operations": [],
    }
    with pytest.raises(ValidationError):
        ProductDto.model_validate(payload)


def test_dump_uses_enum_names_not_values():
    product = product_from_run(build_worked_run()[0])
    dto = product_to_dto(product)
    first_op = dto.blocks[0].operations[0]
    if hasattr(first_op, "chroma"):
        assert isinstance(first_op.chroma, str)
        assert first_op.chroma == "FOUR_ZERO"


def test_order_id_dumps_as_int():
    product = product_from_run(build_worked_run()[0])
    order = Order(id=OrderID(7), product=product, count=3)
    assert order_to_dto(order).id == 7


def test_reference_round_trip():
    ref = reference_from_dto(
        ReferenceDto(name="n", description="d", order_id=5),
    )
    dto = reference_to_dto(ref)
    assert dto.order_id == 5
