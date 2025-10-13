from pydantic import BaseModel

from backend.models import Status


class ChangePayload(BaseModel):
    order_id: int
    new_status: Status
