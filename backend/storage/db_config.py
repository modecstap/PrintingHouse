from urllib.parse import quote_plus

from pydantic import BaseModel


class DBConfig(BaseModel):
    user: str
    password: str | None
    host: str
    port: int
    db_name: str

    def get_db_url(self, driver: str):
        if not self.password:
            return f'postgresql+{driver}://{self.user}@{self.host}:{self.port}/{self.db_name}?target_session_attrs=read-write'
        return f'postgresql+{driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}'

