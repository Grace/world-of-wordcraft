import glob
import os
import re
from typing import Dict, Type, Optional
from .command import Command

class CommandRegistry:
    _instance = None
    _commands: Dict[str, Type[Command]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._commands:
            self._load_commands()

    def _load_commands(self):
        command_path = os.path.join(os.path.dirname(__file__), "**/*.py")
        for file_path in glob.glob(command_path, recursive=True):
            if not file_path.endswith(("__init__.py", "command_registry.py")):
                module_path = os.path.relpath(file_path, os.path.dirname(__file__))
                module_name = os.path.splitext(module_path)[0].replace(os.sep, '.')
                try:
                    module = __import__(f"app.modules.commands.{module_name}", fromlist=['*'])
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, Command) and 
                            attr != Command):
                            cmd = attr()
                            self._commands[cmd.name] = attr
                except Exception as e:
                    print(f"Error loading command {module_name}: {e}")

    def sanitize_command(self, text: str) -> str:
        return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

    def is_valid_command(self, command: str) -> bool:
        return command in self._commands

    def get_command(self, command: str) -> Optional[Type[Command]]:
        return self._commands.get(command)

    @property
    def commands(self) -> Dict[str, Type[Command]]:
        return self._commands