from ..command import Command
from ...network.websocket_message import WebSocketMessage
from ...network.session_manager import SessionManager

class SpeechRateCommand(Command):
    name = "speech-rate"
    description = "Change text-to-speech rate"
    requires_login = False
    MIN_RATE = 0.1
    MAX_RATE = 10.0

    async def execute(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        try:
            rate = float(args.strip())
            if not (self.MIN_RATE <= rate <= self.MAX_RATE):
                return WebSocketMessage(
                    type='error',
                    message=f'Speech rate must be between {self.MIN_RATE} and {self.MAX_RATE}'
                )

            return WebSocketMessage(
                type='speech-rate',
                message=f'Speech rate set to {rate}',
                data={'speechRate': rate}
            )
        except ValueError:
            return WebSocketMessage(
                type='error',
                message=f'Usage: speech-rate <{self.MIN_RATE}-{self.MAX_RATE}>'
            )