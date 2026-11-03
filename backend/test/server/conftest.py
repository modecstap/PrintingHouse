from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine

from backend.server.app import app
from backend.storage.sync_engine import create_sync_engine


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    sync_engine = create_sync_engine()
    try:
        yield sync_engine
    finally:
        sync_engine.dispose()


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    # Один цикл на сессию серверных тестов: async-движок приложения
    # не переживает закрытие портала TestClient.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
