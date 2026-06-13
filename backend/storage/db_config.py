import os
from pathlib import Path

from dotenv import dotenv_values

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

    @classmethod
    def from_dotenv(cls, path_to_env: str | Path) -> "DBConfig":
        env = dotenv_values(path_to_env)
        print(path_to_env)

        return cls(
            user=env["DB_USER"],
            password=env.get("DB_PASSWORD"),
            host=env["DB_HOST"],
            port=int(env["DB_PORT"]),
            db_name=env["DB_NAME"],
        )

    @classmethod
    def from_env(cls) -> "DBConfig":
        return cls(
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            db_name=os.getenv("DB_NAME", "postgres")
        )
