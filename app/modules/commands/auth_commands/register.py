from ..command import Command
from ...database.sqlite_handler import SQLiteHandler
from ...network.websocket_message import WebSocketMessage
from ...network.session_manager import SessionManager
import logging

logger = logging.getLogger(__name__)

class RegisterCommand(Command):
    name = "register"
    description = "Register a new account"
    requires_login = False

    def __init__(self):
        super().__init__()
        self.db = SQLiteHandler()

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        # Parse args
        parts = args.split()
        if len(parts) != 2:
            return WebSocketMessage(
                type='error',
                message='Usage: register <username> <password>'
            )

        username, password = parts

        # Attempt registration
        success, message = await self.db.register_user(username, password)
        if success:
            # Create session and login user automatically
            session_manager.create_session(client_id, username)
            return WebSocketMessage(
                type='success',
                message=f'Welcome to World of Wordcraft, {username}! You are now logged in.'
            )

        return WebSocketMessage(
            type='error',
            message=message
        )