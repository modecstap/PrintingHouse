from pydantic import BaseModel

from backend.models import PressSheet, Chroma, Lamination, ListSize


class InstructionPayload(BaseModel):
    order_id: int
    density: int
    press_sheet: PressSheet
    chroma: Chroma
    lamination: Lamination
    die_cutting: bool
    edition_count: int
    list_size: ListSize
    fitting_count: int
