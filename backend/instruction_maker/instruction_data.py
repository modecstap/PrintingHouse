from pydantic import BaseModel

from backend.models import Chroma, Lamination


class InstructionModel(BaseModel):
    order_id: int | str
    density: int
    chroma: Chroma
    lamination: Lamination
    die_cutting: bool
    sheet_count: int
    fitting_count: int
