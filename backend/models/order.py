from datetime import datetime

from pydantic import BaseModel, Field

from backend.models import Economy, Operation, Printing
from backend.models.order_cost_report import OrderCostReport
from backend.models.status import Status


class Order(BaseModel):
    id: int | None = None
    creation_date: datetime = Field(default=datetime.now())
    status: Status = Field(default=Status.SAVED)
    comment: str = Field(default="")
    unit_count: int = Field(default=1)

    cost_report: OrderCostReport | None = None

    printings: list[Printing]
    operations: list[Operation] = Field(default=[])
    economy: Economy
