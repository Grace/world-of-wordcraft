from typing import Optional

from fastapi import WebSocket
from .connection_manager import ConnectionManager
from .session_manager import SessionManager
from .command_handler import CommandHandler
from .websocket_message import WebSocketMessage
from ..constants import WELCOME_MESSAGE
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WebSocketManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.connection_manager = ConnectionManager()
            self.session_manager = SessionManager()
            self.command_handler = CommandHandler(self.session_manager)
            self.initialized = True

    async def connect(self, websocket: WebSocket) -> str:
        client_id = await self.connection_manager.connect(websocket)
        self.session_manager.create_session(client_id, None)
        welcome = WebSocketMessage(type='welcome', message=WELCOME_MESSAGE)
        await websocket.send_json(welcome.to_dict())
        return client_id

    async def disconnect(self, websocket: WebSocket):
        client_id = self._get_client_id(websocket)
        if client_id:
            await self.connection_manager.disconnect(client_id)
            self.session_manager.end_session(client_id)

    async def handle_message(self, websocket: WebSocket, message: str) -> WebSocketMessage:
        client_id = self._get_client_id(websocket)
        if not client_id:
            return WebSocketMessage(type='error', message='Connection error')

        command_name, args = self.command_handler.parse_command(message)
        is_logged_in = self.session_manager.is_logged_in(client_id)
        
        return await self.command_handler.execute_command(command_name, args, is_logged_in)

    def get_websocket_by_username(self, username: str) -> Optional[WebSocket]:
        for client_id, websocket in self.connection_manager.active_connections.items():
            if self.session_manager.get_username(client_id) == username:
                return websocket
        return None

    def _get_client_id(self, websocket: WebSocket) -> str:
        for cid, ws in self.connection_manager.active_connections.items():
            if ws == websocket:
                return cid
        return None