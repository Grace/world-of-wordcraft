from .commands.commands_registry import CommandsRegistry

class CommandRegistry:
    def __init__(self):
        self.commands = {}
        self._load_commands()

    def _load_commands(self):
        self.commands = CommandsRegistry.get_commands()

    def sanitize_command(self, text: str) -> str:
        return text.strip().lower()