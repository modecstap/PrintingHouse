from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from backend.models import CostReport, Edition
from backend.models.status import Status


class Order(BaseModel):
    id: int | None = None
    creation_date: datetime
    status: Status
    comment: str
    cost_report: CostReport
    edition: Edition
    markup: Decimal
    paper_cost: Decimal
