from pydantic import BaseModel

from backend.models import Chroma, Lamination, PressSheet, ListSize


class InstructionModel(BaseModel):
    order_id: int | str
    unit_count: int
    comment: str
    density: int
    press_sheet: PressSheet
    chroma: Chroma
    lamination: Lamination
    die_cutting: bool
    sheet_count: int
    fitting_count: int
    edition_count: int
    list_size: ListSize
    product_per_sheet: int
