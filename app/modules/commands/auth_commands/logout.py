from ..command import Command
from ...network.websocket_message import WebSocketMessage
from ...constants import WELCOME_MESSAGE
import logging

logger = logging.getLogger(__name__)

class LogoutCommand(Command):
    def __init__(self):
        super().__init__(
            name="logout",
            description="Logout from your current session"
        )

    async def execute(self, args: str = "") -> WebSocketMessage:
        logger.info("Player logging out")
        
        # Return welcome message with login instructions
        logout_message = (
            "You have been logged out.\n\n" +
            WELCOME_MESSAGE
        )
        
        return WebSocketMessage(
            type='logout',
            message=logout_message
        )