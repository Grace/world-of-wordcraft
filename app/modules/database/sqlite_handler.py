import logging
from typing import Tuple

from starlette.websockets import WebSocket

from .db_connection import DatabaseConnection
from .user_repository import UserRepository

logger = logging.getLogger(__name__)

class SQLiteHandler:
    def __init__(self, db_path: str = "game.db"):
        self.db = DatabaseConnection(db_path)
        self.users = UserRepository(self.db)

    async def init_db(self):
        try:
            async with self.db.connect() as conn:
                with open('app/schema.sql', 'r') as f:
                    schema_sql = f.read()
                await conn.executescript(schema_sql)
                await conn.commit()
            logger.info("Database initialized with schema")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    async def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        return await self.users.create_user(username, password)

    async def verify_login(self, username: str, password: str) -> Tuple[bool, str]:
        return await self.users.verify_user(username, password)

    async def close(self):
        await self.db.close()