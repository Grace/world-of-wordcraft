from ..modules.database.sqlite_handler import SQLiteHandler
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.db = SQLiteHandler()
        
    async def startup(self):
        await self.db.init_db()
        logger.info("Database initialized")
        
    async def shutdown(self):
        await self.db.close()
        logger.info("Database connection closed")