from pydantic import BaseModel, Field


class CutterInfo(BaseModel):
    stack_height: int = Field(description="Высота стопки помещающейся в резаке в мм")
