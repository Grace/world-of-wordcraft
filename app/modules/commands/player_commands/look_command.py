from ..player_command import PlayerCommand
from ...roles import Role
from ...network.websocket_message import WebSocketMessage
from ...network.session_manager import SessionManager
from ...decorators import required_roles

class LookCommand(PlayerCommand):
    name = "look"
    description = "Look around your current location"

    @required_roles([Role.PLAYER])
    async def handle(self, args: str, client_id: str, session_manager: SessionManager) -> WebSocketMessage:
        return WebSocketMessage(
            type='look',
            message='You look around...'
        )