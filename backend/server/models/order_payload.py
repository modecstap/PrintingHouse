from pydantic import BaseModel

from backend.models import Edition, Production


class OrderPayload(BaseModel):
    comment: str
    edition: Edition
    production: Production
