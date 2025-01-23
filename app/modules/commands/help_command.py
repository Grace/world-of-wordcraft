from .command import Command
from ..network.websocket_message import WebSocketMessage
import logging

logger = logging.getLogger(__name__)

class HelpCommand(Command):
    def __init__(self):
        super().__init__(name="help", description="Get help about available commands")
        self.command_details = {
            'help': {
                'usage': 'help <command_name>',
                'description': 'Shows help for a specific command or lists all commands'
            },
            'register': {
                'usage': 'register <username> <password>',
                'description': 'Create a new player account'
            },
            'login': {
                'usage': 'login <username> <password>',
                'description': 'Login to an existing account'
            },
            'highcontrast': {
                'usage': 'highcontrast <on|off>',
                'description': 'Toggle high contrast mode'
            },
            'fontsize': {
                'usage': 'fontsize <number>',
                'description': 'Change the font size'
            },
            'speech': {
                'usage': 'speech <on|off>',
                'description': 'Toggle speech synthesis'
            }
        }

    async def execute(self, args: str) -> WebSocketMessage:
        command = args.strip().lower()
        
        # If no specific command requested, show all commands
        if not command:
            help_text = "Available commands:\n\n"
            for cmd, details in self.command_details.items():
                help_text += f"{cmd}: {details['description']}\n"
            help_text += "\nType 'help <command>' for more details about a specific command."
            return WebSocketMessage(type='help', message=help_text)
            
        # Show help for specific command
        if command in self.command_details:
            details = self.command_details[command]
            help_text = f"Command: {command}\n"
            help_text += f"Usage: {details['usage']}\n"
            help_text += f"Description: {details['description']}"
            return WebSocketMessage(type='help', message=help_text)
            
        return WebSocketMessage(
            type='error',
            message=f"Unknown command: {command}. Type 'help' to see all commands."
        )