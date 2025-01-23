from ..modules.network.websocket_manager import WebSocketManager
import logging

logger = logging.getLogger(__name__)

class WebsocketService:
    def __init__(self):
        self.manager = WebSocketManager()
        
    async def startup(self):
        logger.info("WebSocket service initialized")
        
    async def shutdown(self):
        # Cleanup any active connections
        await self.manager.close_all()
        logger.info("WebSocket service shutdown")