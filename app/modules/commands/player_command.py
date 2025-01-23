from abc import abstractmethod
from .command import Command
from ..network.websocket_message import WebSocketMessage
from ..network.session_manager import SessionManager

class PlayerCommand(Command):
    requires_login = True

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        """Execute method matches base class signature"""
        return await self.handle(args, client_id, session_manager)

    @abstractmethod
    async def handle(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        """Handle method matches execute signature"""
        pass