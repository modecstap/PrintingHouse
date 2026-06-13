import asyncio
import os

from backend.storage.database import Database
from backend.storage.db_config import DBConfig
from server.fast_api_server import FastAPIServer
from server.server_config import ServerConfig


async def main():
    await create_db()
    await start_server()


async def create_db():
    config = DBConfig.from_env()
    await Database(config).create_all()


async def start_server():
    host = os.getenv("SERVER_HOST", "localhost")
    port = int(os.getenv("SERVER_PORT", 8080))
    config = ServerConfig(
        host=host,
        port=port
    )
    server = FastAPIServer(
        config=config
    )
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
