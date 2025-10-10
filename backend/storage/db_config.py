from pydantic import BaseModel


class DBConfig(BaseModel):
    user: str
    password: str | None
    host: str
    port: int
    db_name: str
