import asyncio
import os

from server.fast_api_server import FastAPIServer
from server.server_config import ServerConfig


async def main():
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
