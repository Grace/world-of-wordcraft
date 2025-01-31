import aiosqlite
from pathlib import Path
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self, db_path: str = "game.db"):
        self.db_path = Path(db_path)
        self._connection = None

    @asynccontextmanager
    async def connect(self):
        conn = await aiosqlite.connect(self.db_path)
        try:
            self._connection = conn
            yield conn
        finally:
            await conn.close()

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None