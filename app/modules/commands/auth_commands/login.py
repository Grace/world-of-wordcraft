from ..command import Command
from ...database.sqlite_handler import SQLiteHandler
from ...network.websocket_message import WebSocketMessage
import logging

logger = logging.getLogger(__name__)

class LoginCommand(Command):
    def __init__(self):
        super().__init__(name="login", description="Login to an existing account")
        self.db = SQLiteHandler()

    async def execute(self, args: str) -> WebSocketMessage:
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
        
        return WebSocketMessage(
            type='success' if success else 'error',
            message=message
        )