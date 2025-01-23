import glob
import os
import re
from typing import Dict, Optional
from . import ALLOWED_COMMANDS

class CommandRegistry:
    def __init__(self):
        self.commands = {}
        self._load_commands()

    def _load_commands(self):
        # Load predefined allowed commands
        self.commands = ALLOWED_COMMANDS
        
        # Optionally scan command files
        command_path = os.path.join(os.path.dirname(__file__), "commands/*.py")
        for file_path in glob.glob(command_path):
            if not file_path.endswith("__init__.py"):
                command_name = os.path.splitext(os.path.basename(file_path))[0]
                if command_name not in self.commands:
                    self.commands[command_name] = None

    def sanitize_command(self, text: str) -> str:
        return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

    def is_valid_command(self, command: str) -> bool:
        return command in self.commands