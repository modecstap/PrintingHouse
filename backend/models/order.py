from datetime import datetime

from pydantic import BaseModel, Field

from backend.models import CostReport, Edition, Production
from backend.models.status import Status


class Order(BaseModel):
    id: int | None = None
    creation_date: datetime = Field(default=datetime.now())
    status: Status
    comment: str
    cost_report: CostReport
    edition: Edition
    production: Production

    class Config:
        use_enum_values = False
        json_encoders = {
            Status: lambda v: v.name  # возвращаем name вместо value
        }
