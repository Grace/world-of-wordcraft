from ..command import Command
from ...network.websocket_message import WebSocketMessage
from ...network.session_manager import SessionManager

class SpeechCommand(Command):
    name = "speech"
    description = "Control text-to-speech settings"
    requires_login = False

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        param = args.strip().lower()

        if not param or param not in ['on', 'off']:
            return WebSocketMessage(
                type='error',
                message='Usage: speech <on|off>'
            )

        return WebSocketMessage(
            type='speech',
            message=f'Text-to-speech turned {param}',
            data={'speech': param}
        )