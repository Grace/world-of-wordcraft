import logging
import re
from typing import Dict, Type, Optional
from .command import Command
from .player_commands.look_command import LookCommand
from .auth_commands.login import LoginCommand
from .auth_commands.logout import LogoutCommand
from .auth_commands.register import RegisterCommand
from .help_command import HelpCommand
from .accessibility_commands.highcontrast_command import HighContrastCommand
from .accessibility_commands.fontsize_command import FontSizeCommand
from .accessibility_commands.speech_command import SpeechCommand
from .accessibility_commands.speech_rate_command import SpeechRateCommand
from .accessibility_commands.speech_repeat_command import SpeechRepeatCommand
from .accessibility_commands.speech_stop_command import SpeechStopCommand

logger = logging.getLogger(__name__)

class CommandRegistry:
    _instance = None
    _commands: Dict[str, Type[Command]] = {}
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._loaded:
            self._load_commands()
            self._loaded = True

    def _load_commands(self):
        """Load and register all available commands"""
        command_classes = {
            'help': HelpCommand,
            'login': LoginCommand,
            'logout': LogoutCommand,
            'register': RegisterCommand,
            'look': LookCommand,
            'highcontrast': HighContrastCommand,
            'fontsize': FontSizeCommand,
            'speech': SpeechCommand,
            'speech-rate': SpeechRateCommand,
            'speech-repeat': SpeechRepeatCommand,
            'speech-stop': SpeechStopCommand
        }

        for cmd_name, cmd_class in command_classes.items():
            try:
                # Verify command class inheritance
                if not issubclass(cmd_class, Command):
                    raise ValueError(f"{cmd_class.__name__} is not a Command subclass")
                
                # Register command
                self._commands[cmd_name] = cmd_class
                logger.info(f"Registered command: {cmd_name}")
                
            except Exception as e:
                logger.error(f"Error registering command {cmd_name}: {e}")

        logger.info(f"Available commands: {', '.join(self._commands.keys())}")

    def sanitize_command(self, text: str) -> str:
        return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

    def is_valid_command(self, command: str) -> bool:
        return command.lower() in self._commands

    def get_command(self, name: str) -> Optional[Type[Command]]:
        """Get command class by name"""
        command = self._commands.get(name.lower())
        if not command:
            logger.warning(f"Command not found: {name}")
        return command

    @property
    def commands(self) -> Dict[str, Type[Command]]:
        return self._commands.copy()