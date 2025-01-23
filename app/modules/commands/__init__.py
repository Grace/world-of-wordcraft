from .help_command import HelpCommand
from .auth_commands.login import LoginCommand
from .auth_commands.register import RegisterCommand
from .auth_commands.logout import LogoutCommand
from .commands_registry import CommandsRegistry

# Register commands
registry = CommandsRegistry()
registry.register('help', HelpCommand)
registry.register('login', LoginCommand)
registry.register('register', RegisterCommand)
registry.register('logout', LogoutCommand)