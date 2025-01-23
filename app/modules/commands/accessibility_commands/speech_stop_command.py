from ..command import Command
from ...network.websocket_message import WebSocketMessage
from ...network.session_manager import SessionManager

class SpeechStopCommand(Command):
    name = "speech-stop"
    description = "Stop any ongoing text-to-speech"
    requires_login = False

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        return WebSocketMessage(
            type='speech-stop',
            message='Stopping text-to-speech...',
            data={'stop': True}
        )