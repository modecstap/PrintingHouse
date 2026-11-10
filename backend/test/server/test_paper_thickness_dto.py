"""PaperDto thickness validation."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.new_core import Format, Paper, Sheet
from backend.new_core.materials.sheet import SheetID
from backend.new_core.values.money import Money
from backend.server.catalog_mapping import sheet_from_write_dto, sheet_to_read_dto
from backend.server.schemas import PaperDto, SheetDto


def test_paper_dto_accepts_fractional_thickness():
    dto = PaperDto.model_validate(
        {
            "density": 80,
            "thickness": 0.15,
            "name": "офсет",
            "price_per_kilo": "90",
        },
    )
    assert dto.thickness == Decimal("0.15")


@pytest.mark.parametrize("thickness", [0, 0.151])
def test_paper_dto_rejects_invalid_thickness(thickness):
    with pytest.raises(ValidationError):
        PaperDto.model_validate(
            {
                "density": 80,
                "thickness": thickness,
                "name": "офсет",
                "price_per_kilo": "90",
            },
        )


def test_sheet_dto_round_trip_fractional_thickness():
    sheet = Sheet(
        id=SheetID(1),
        paper=Paper(
            density=80,
            thickness=Decimal("0.15"),
            name="офсет",
            price_per_kilo=Money(Decimal("90")),
        ),
        format=Format(name="SRA3", height=450, width=320),
    )
    dto = sheet_to_read_dto(sheet)
    assert dto.paper.thickness == Decimal("0.15")

    write = SheetDto.model_validate(dto.model_dump())
    paper, _fmt = sheet_from_write_dto(write)
    assert paper.thickness == Decimal("0.15")
