from .command import Command
from ..network.websocket_message import WebSocketMessage
from ..network.session_manager import SessionManager
import logging

logger = logging.getLogger(__name__)

class HelpCommand(Command):
    name = "help"
    description = "Get help about available commands"
    requires_login = False

    GENERAL_COMMANDS = {
        'help': 'Usage: help [command]\nGet help about commands\n',
        'login': 'Usage: login <username> <password>\nLogin to your account\n',
        'register': 'Usage: register <username> <password>\nCreate a new account\n',
        'highcontrast': 'Usage: highcontrast <on|off>\nToggle high contrast theme\n',
        'fontsize': 'Usage: fontsize <number>\nChange the game text font size\n',
    }

    PLAYER_COMMANDS = {
        'logout': 'Usage: logout\nLog out of your account\n',
        'look': 'Usage: look\nLook around your current location\n',
        'speech': 'Usage: speech <on|off>\nToggle text-to-speech output\n',
        'speech-rate': 'Usage: speech-rate <0.1-10>\nChange text-to-speech playback rate\n',
        'speech-repeat': 'Usage: speech-repeat\nRepeat all visible game text using text-to-speech\n',
        'speech-stop': 'Usage: speech-stop\nStop any ongoing text-to-speech\n'
    }

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        command = args.strip().lower()
        is_logged_in = session_manager.is_logged_in(client_id)
        
        # Combine available commands based on login status
        available_commands = self.GENERAL_COMMANDS.copy()
        if is_logged_in:
            available_commands.update(self.PLAYER_COMMANDS)

        # Show specific command help if provided
        if command:
            if command in available_commands:
                help_text = f"Command: {command}\n{available_commands[command]}"
                return WebSocketMessage(
                    type="help",
                    message=help_text
                )
            return WebSocketMessage(
                type="error",
                message=f"Unknown command: {command}"
            )

        # List all available commands with descriptions
        commands_list = "Available Commands:\n\n"
        for cmd, desc in sorted(available_commands.items()):
            commands_list += f"{cmd}: {desc}\n"
        
        return WebSocketMessage(
            type="help",
            message=commands_list
        )