"""JSON mapping round-trip and validation rules."""

from dataclasses import replace

import pytest
from pydantic import ValidationError

from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.operations.laminate.laminate import Laminate
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.product import Product
from backend.new_core.part import Part
from backend.new_core.values.percent import Percent
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
    run, _, _, _, _ = build_worked_run(with_cut=False)
    block: Part = replace(
        run.block,
        operations=run.block.operations + (DieCut(operator_id=DieCutterOperatorID(2)),),
    )
    return Product(
        parts_markup=Percent(0),
        blocks=(block,),
        operations=product_from_run(run).operations,
    )


def _sample_imposition() -> dict:
    product = product_from_run(build_worked_run()[0])
    return product_to_dto(product).model_dump()["blocks"][0]["imposition"]


def test_product_dto_embeds_press_sheet():
    product = _product_with_die_cut()
    dumped = product_to_dto(product).model_dump()
    imp = dumped["blocks"][0]["imposition"]
    assert "press_sheet" in imp
    assert "id" in imp["press_sheet"]
    assert "sheet_id" not in imp
    laminate_ops = [op for op in dumped["blocks"][0]
                    ["operations"] if op["kind"] == "laminate"]
    assert laminate_ops
    assert "film_id" in laminate_ops[0]
    assert "film" not in laminate_ops[0]


def test_product_from_dto_round_trips_press_sheet():
    product = _product_with_die_cut()
    restored = product_from_dto(product_to_dto(product))
    original = product.blocks[0]
    block = restored.blocks[0]
    assert block.imposition.press_sheet == original.imposition.press_sheet
    orig_laminate = next(
        op for op in original.operations if isinstance(
            op, Laminate))
    rest_laminate = next(
        op for op in block.operations if isinstance(
            op, Laminate))
    assert rest_laminate.film_id == orig_laminate.film_id


def test_imposition_extra_fields_ignored():
    product = product_from_run(build_worked_run()[0])
    dumped = product_to_dto(product).model_dump()
    dumped["blocks"][0]["imposition"]["ignored_field"] = 1
    dto = ProductDto.model_validate(dumped)
    block = product_from_dto(dto).blocks[0]
    assert block.imposition.press_sheet == product.blocks[0].imposition.press_sheet


def test_unknown_kind_rejected():
    payload = {
        "parts_markup": 0,
        "blocks": [
            {
                "imposition": _sample_imposition(),
                "count": 1,
                "operations": [{"kind": "unknown", "operator_id": 1}],
            }
        ],
        "operations": [],
    }
    with pytest.raises(ValidationError):
        ProductDto.model_validate(payload)


def test_block_markup_field_rejected():
    payload = {
        "parts_markup": 0,
        "blocks": [
            {
                "imposition": _sample_imposition(),
                "count": 1,
                "markup": 5,
                "operations": [],
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
        description="визитки",
        created_at=TEST_ORDER_CREATED_AT,
    )
    dto = order_to_dto(order)
    assert dto.id == 7
    assert dto.description == "визитки"
    assert dto.created_at == TEST_ORDER_CREATED_AT


def test_reference_round_trip():
    ref = reference_from_dto(
        ReferenceDto(name="n", description="d", order_id=5),
    )
    dto = reference_to_dto(ref)
    assert dto.order_id == 5
