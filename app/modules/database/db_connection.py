import aiosqlite
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self, db_path: str = "game.db"):
        self.db_path = Path(db_path)
        self._pool = None

    async def connect(self):
        if not self._pool:
            self._pool = await aiosqlite.connect(self.db_path)
        return self._pool

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None