"""HTTP listen address."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ServerConfig:
    """Host and port for uvicorn."""

    host: str
    port: int
