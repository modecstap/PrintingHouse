from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from backend.models import CostReport, Edition
from backend.models.status import Status


class Order(BaseModel):
    id: int | None = None
    creation_date: datetime = Field(default=datetime.now())
    status: Status
    comment: str
    cost_report: CostReport
    edition: Edition
    markup: Decimal
    paper_cost: Decimal

    class Config:
        use_enum_values = False
        json_encoders = {
            Status: lambda v: v.name  # возвращаем name вместо value
        }
