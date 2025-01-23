from ..command import Command
from ...network.websocket_message import WebSocketMessage
from ...network.session_manager import SessionManager

class FontSizeCommand(Command):
    name = "fontsize"
    description = "Change the game text font size"
    requires_login = False
    MIN_SIZE = 1
    MAX_SIZE = 1000

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        try:
            size = int(args.strip())
            if not (self.MIN_SIZE <= size <= self.MAX_SIZE):
                return WebSocketMessage(
                    type='error',
                    message=f'Font size must be between {self.MIN_SIZE} and {self.MAX_SIZE}'
                )

            return WebSocketMessage(
                type='fontsize',
                message=f'Font size set to {size}px',
                data={'fontSize': size}
            )
        except ValueError:
            return WebSocketMessage(
                type='error',
                message=f'Usage: fontsize <{self.MIN_SIZE}-{self.MAX_SIZE}>'
            )