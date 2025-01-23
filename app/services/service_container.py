import logging

from .database_service import DatabaseService
from .websocket_service import WebsocketService

logger = logging.getLogger(__name__)

class ServiceContainer:
    def __init__(self):
        self.database = DatabaseService()
        self.websocket = WebsocketService()
        
    async def startup(self):
        """Initialize all services"""
        await self.database.startup()
        await self.websocket.startup()
        logger.info("All services initialized")
        
    async def shutdown(self):
        """Cleanup all services"""
        await self.websocket.shutdown()
        await self.database.shutdown()
        logger.info("All services shutdown")