from ..command import Command
from ...network.websocket_message import WebSocketMessage
from ...network.session_manager import SessionManager

class HighContrastCommand(Command):
    name = "highcontrast"
    description = "Toggle high contrast mode (on/off)"
    requires_login = False

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        param = args.strip().lower()
        
        if param not in ['on', 'off']:
            return WebSocketMessage(
                type='error',
                message='Usage: highcontrast <on|off>'
            )

        theme = 'high-contrast' if param == 'on' else 'default'
        
        return WebSocketMessage(
            type='theme',
            message=f'High contrast mode turned {param}',
            data={'theme': theme}
        )