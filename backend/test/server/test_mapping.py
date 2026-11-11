"""JSON mapping round-trip and validation rules."""

from dataclasses import replace

import pytest
from pydantic import ValidationError

from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.operations.laminate.laminate import Laminate
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.product import Product
from backend.new_core.part import Part
from backend.new_core.personal.die_cutter_operator import DieCutterOperatorID
from backend.server.mapping import (
    order_to_dto,
    product_from_dto,
    product_to_dto,
    reference_from_dto,
    reference_to_dto,
)
from backend.server.schemas import ProductDto, ReferenceDto
from backend.test.new_core.test_print_run import build_worked_run
from backend.test.storage.helpers import TEST_ORDER_CREATED_AT, product_from_run


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


def test_product_dto_uses_catalog_ids_only():
    product = _product_with_die_cut()
    dumped = product_to_dto(product).model_dump()
    imp = dumped["blocks"][0]["imposition"]
    assert "sheet_id" in imp
    assert "press_sheet" not in imp
    laminate_ops = [
        op for op in dumped["blocks"][0]["operations"] if op["kind"] == "laminate"
    ]
    assert laminate_ops
    assert "film_id" in laminate_ops[0]
    assert "film" not in laminate_ops[0]


def test_product_from_dto_restores_ids_unhydrated_sheet():
    product = _product_with_die_cut()
    restored = product_from_dto(product_to_dto(product))
    original = product.blocks[0]
    block = restored.blocks[0]
    assert block.imposition.sheet_id == original.imposition.sheet_id
    assert block.imposition.press_sheet is None
    orig_laminate = next(op for op in original.operations if isinstance(op, Laminate))
    rest_laminate = next(op for op in block.operations if isinstance(op, Laminate))
    assert rest_laminate.film_id == orig_laminate.film_id


def test_extra_nested_press_sheet_ignored():
    product = product_from_run(build_worked_run()[0])
    dumped = product_to_dto(product).model_dump()
    dumped["blocks"][0]["imposition"]["press_sheet"] = {
        "paper": {
            "density": 100,
            "thickness": 1,
            "name": "ignored",
            "price_per_kilo": "1",
        },
        "format": {"name": "f", "height": 1, "width": 1},
    }
    dto = ProductDto.model_validate(dumped)
    block = product_from_dto(dto).blocks[0]
    assert block.imposition.press_sheet is None
    assert block.imposition.sheet_id.value == dumped["blocks"][0]["imposition"]["sheet_id"]


def test_unknown_kind_rejected():
    payload = {
        "blocks": [
            {
                "imposition": {
                    "target": {"name": "t", "height": 10, "width": 10},
                    "sheet_id": 1,
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
    order = Order(
        id=OrderID(7),
        product=product,
        count=3,
        description="",
        created_at=TEST_ORDER_CREATED_AT,
    )
    assert order_to_dto(order).id == 7


def test_reference_round_trip():
    ref = reference_from_dto(
        ReferenceDto(name="n", description="d", order_id=5),
    )
    dto = reference_to_dto(ref)
    assert dto.order_id == 5
