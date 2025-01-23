from .auth_commands.login import LoginCommand
from .auth_commands.register import RegisterCommand

ALLOWED_COMMANDS = {
    'login': LoginCommand,
    'register': RegisterCommand
}