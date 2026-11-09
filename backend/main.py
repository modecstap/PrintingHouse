import asyncio
import os
import sys

from backend.auth import AdminSeedConfigError, AuthConfig, MissingJwtSecret, seed_admin_if_empty
from backend.server.app import serve
from backend.server.server_config import ServerConfig
from backend.storage.database import Database
from backend.storage.db_config import DBConfig
from backend.storage.user.repository import SqlUserRepository


async def main() -> None:
    try:
        await wait_for_database()
        await start_server()
    except (MissingJwtSecret, AdminSeedConfigError) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


async def wait_for_database() -> None:
    config = DBConfig.from_env()
    await Database(config).wait_for_connection()


async def start_server() -> None:
    auth_config = AuthConfig.from_env()
    db_config = DBConfig.from_env()
    database = Database(db_config)
    with database.session_factory() as session:
        seed_admin_if_empty(
            SqlUserRepository(session),
            os.getenv("ADMIN_USERNAME"),
            os.getenv("ADMIN_PASSWORD"),
        )
        session.commit()
    server_config = ServerConfig(
        host=os.getenv("SERVER_HOST", "localhost"),
        port=int(os.getenv("SERVER_PORT", "8080")),
    )
    await serve(server_config, auth_config=auth_config, database=database)


if __name__ == "__main__":
    asyncio.run(main())
