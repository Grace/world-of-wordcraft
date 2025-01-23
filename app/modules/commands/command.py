from abc import ABC, abstractmethod
from ..network.websocket_message import WebSocketMessage
from ..network.session_manager import SessionManager

class Command(ABC):
    name = ""
    description = ""
    requires_login = False

    def __init__(self):
        if not self.name or not self.description:
            raise ValueError("Commands must define name and description class attributes")

    @abstractmethod
    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        """Base execute method that all commands must implement with consistent signature"""
        pass