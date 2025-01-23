from ..command import Command
from ...network.websocket_message import WebSocketMessage
from ...network.session_manager import SessionManager

class SpeechRepeatCommand(Command):
    name = "speech-repeat"
    description = "Repeat all visible game text using text-to-speech"
    requires_login = False

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        return WebSocketMessage(
            type='speech-repeat',
            message='Repeating all visible text...',
            data={'repeat': True}
        )