from typing import Dict, Type
from .command import Command

class CommandsRegistry:
    _instance = None
    _commands = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, name: str, command_class: Type[Command]):
        cls._commands[name] = command_class

    @classmethod
    def get_commands(cls) -> Dict[str, Type[Command]]:
        return cls._commands