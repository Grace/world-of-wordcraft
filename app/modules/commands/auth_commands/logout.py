from ..command import Command
from ...network.websocket_message import WebSocketMessage
from ...network.session_manager import SessionManager
from ...constants import WELCOME_MESSAGE
import logging

logger = logging.getLogger(__name__)

class LogoutCommand(Command):
    name = "logout"
    description = "Logout from your current session"
    requires_login = True

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        session_manager.end_session(client_id)
        return WebSocketMessage(
            type='logout',
            message='You have been logged out.\n\n' + WELCOME_MESSAGE
        )