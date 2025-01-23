from ..command import Command
from ..roles import Role
from ...database.sqlite_handler import SQLiteHandler
from ...network.websocket_message import WebSocketMessage
from ...network.session_manager import SessionManager
from ..decorators import required_roles
import logging

logger = logging.getLogger(__name__)

class LoginCommand(Command):
    name = "login"
    description = "Login to your account"
    requires_login = False

    def __init__(self):
        super().__init__()
        self.db = SQLiteHandler()

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        # Parse username and password
        parts = args.split()
        if len(parts) != 2:
            return WebSocketMessage(
                type='error',
                message='Usage: login <username> <password>'
            )

        username, password = parts
        logger.debug(f"Attempting login for user: {username}")

        # Attempt login
        success, message = await self.db.verify_login(username, password)
        
        if success:
            session_manager.create_session(client_id, username)
            return WebSocketMessage(
                type='success',
                message=f'Welcome back, {username}!'
            )
            
        return WebSocketMessage(
            type='error',
            message=message
        )