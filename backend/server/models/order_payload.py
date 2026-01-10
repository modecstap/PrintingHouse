from pydantic import BaseModel

from backend.models import Edition, Production, Economy


class OrderPayload(BaseModel):
    comment: str
    edition: Edition
    production: Production
    economy: Economy
