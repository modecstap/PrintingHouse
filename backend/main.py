import asyncio

from server.fast_api_server import FastAPIServer
from server.server_config import ServerConfig


async def main():
    config = ServerConfig(
        host="localhost",
        port=8080
    )
    server = FastAPIServer(
        config=config
    )
    server.save_openapi_description()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
