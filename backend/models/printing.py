from pydantic import BaseModel

from backend.models import Edition, Production, PrintingCostReport


class Printing(BaseModel):
    edition: Edition
    production: Production
    cost_report: PrintingCostReport | None = None
    comment: str | None = None
