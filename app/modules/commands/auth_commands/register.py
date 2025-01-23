from ..command import Command
from ...database.sqlite_handler import SQLiteHandler
from ...network.websocket_message import WebSocketMessage
import re
import logging

logger = logging.getLogger(__name__)

class RegisterCommand(Command):
    def __init__(self):
        super().__init__(name="register", description="Register a new account")
        self.db = SQLiteHandler()

    async def execute(self, args: str) -> WebSocketMessage:
        parts = args.split()
        if len(parts) != 2:
            return WebSocketMessage(
                type='error',
                message='Usage: register <username> <password>'
            )

        username, password = parts
        logger.debug(f"Validating - username length: {len(username)}, password length: {len(password)}")

        # Validate with detailed error messages
        if len(username) < 3:
            return WebSocketMessage(type='error', message='Username must be at least 3 characters')
        if len(username) > 20:
            return WebSocketMessage(type='error', message='Username must be less than 20 characters')
        if len(password) < 6:
            return WebSocketMessage(type='error', message='Password must be at least 6 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return WebSocketMessage(type='error', message='Username can only contain letters, numbers, and underscore')

        # If we get here, validation passed
        success, message = await self.db.create_player(username, password)
        return WebSocketMessage(
            type='success' if success else 'error',
            message=message
        )

    def _validate_input(self, username: str, password: str) -> bool:
        return (
            3 <= len(username) <= 20 and
            len(password) >= 6 and
            re.match(r'^[a-zA-Z0-9_]+$', username)
        )