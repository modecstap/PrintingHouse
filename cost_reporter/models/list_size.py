from pydantic import BaseModel


class ListSize(BaseModel):
    height: int
    width: int
    bleeds: int
