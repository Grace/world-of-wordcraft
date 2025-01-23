import aiosqlite
import bcrypt
from pathlib import Path
import logging
import re
from typing import Tuple
from .db_connection import DatabaseConnection
from .user_repository import UserRepository

logger = logging.getLogger(__name__)

class SQLiteHandler:
    def __init__(self, db_path: str = "game.db"):
        self.db = DatabaseConnection(db_path)
        self.users = UserRepository(self.db)

    async def init_db(self):
        await self.users.create_tables()

    async def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        return await self.users.create_user(username, password)

    async def verify_login(self, username: str, password: str) -> Tuple[bool, str]:
        return await self.users.verify_user(username, password)

    async def close(self):
        await self.db.close()