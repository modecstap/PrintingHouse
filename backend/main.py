import asyncio
import os

from backend.server.app import serve
from backend.server.server_config import ServerConfig
from backend.storage.database import Database
from backend.storage.db_config import DBConfig


async def main():
    await wait_for_database()
    await start_server()


async def wait_for_database():
    config = DBConfig.from_env()
    await Database(config).wait_for_connection()


async def start_server():
    host = os.getenv("SERVER_HOST", "localhost")
    port = int(os.getenv("SERVER_PORT", 8080))
    config = ServerConfig(
        host=host,
        port=port
    )
    await serve(config)


if __name__ == "__main__":
    asyncio.run(main())
