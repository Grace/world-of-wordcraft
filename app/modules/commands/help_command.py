from .command import Command
from ..network.websocket_message import WebSocketMessage
from ..network.session_manager import SessionManager
import logging

logger = logging.getLogger(__name__)

class HelpCommand(Command):
    name = "help"
    description = "Get help about available commands"
    requires_login = False

    HELP_TEXTS = {
        'help': 'Usage: help [command]\nGet help about commands',
        'login': 'Usage: login <username> <password>\nLogin to your account',
        'register': 'Usage: register <username> <password>\nCreate a new account',
        'logout': 'Usage: logout\nLog out of your account',
        'look': 'Usage: look\nLook around your current location',
        'highcontrast': 'Usage: highcontrast <on|off>\nToggle high contrast theme'  # Add this line
    }

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        command = args.strip().lower()
        if command and command in self.HELP_TEXTS:
            return WebSocketMessage(
                type='help',
                message=self.HELP_TEXTS[command]
            )
        
        help_text = "Available commands:\n\n"
        for cmd, help_msg in self.HELP_TEXTS.items():
            first_line = help_msg.split('\n')[0]
            help_text += f"{cmd}: {first_line}\n"
        
        return WebSocketMessage(
            type='help',
            message=help_text
        )