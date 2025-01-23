from typing import Tuple
from ..commands.command_registry import CommandRegistry
from .session_manager import SessionManager
from ..network.websocket_message import WebSocketMessage
import logging

logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self, session_manager: SessionManager):
        self.command_registry = CommandRegistry()
        self.session_manager: SessionManager = session_manager

    def parse_command(self, message: str) -> Tuple[str, str]:
        parts = message.strip().split(maxsplit=1)
        command = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        return command, args

    async def execute_command(self, command_name: str, args: str, client_id: str) -> WebSocketMessage:
        try:
            command_class = self.command_registry.get_command(command_name)
            if not command_class:
                return WebSocketMessage(
                    type='error',
                    message=f'Unknown command. Type "help" for available commands.'
                )

            # Check login state from session
            is_logged_in = self.session_manager.is_logged_in(client_id)
            command = command_class()

            if command.requires_login and not is_logged_in:
                return WebSocketMessage(
                    type='error',
                    message='You must be logged in to use this command.'
                )

            return await command.execute(args, client_id, self.session_manager)

        except Exception as e:
            logger.error(f"Command execution error: {str(e)}", exc_info=True)
            return WebSocketMessage(
                type='error',
                message='Error executing command'
            )