from fastapi import WebSocket
from typing import Dict, Set
import logging
from .websocket_message import WebSocketMessage
from ..commands.command_registry import CommandRegistry
from ..constants import WELCOME_MESSAGE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections = {}  # Dictionary of client_id: websocket
        self.logged_in_players = {}   # Dictionary of client_id: player_data
        self.command_registry = CommandRegistry()

    async def connect(self, websocket: WebSocket) -> str:
        await websocket.accept()
        client_id = f"{websocket.client.host}:{websocket.client.port}"
        self.active_connections[client_id] = websocket
        
        # Send welcome message
        welcome = WebSocketMessage(type='welcome', message=WELCOME_MESSAGE)
        await websocket.send_json(welcome.to_dict())
        
        logger.info(f"Client {client_id} connected")
        return client_id

    async def disconnect(self, websocket: WebSocket):
        client_id = next(
            (cid for cid, ws in self.active_connections.items() if ws == websocket),
            None
        )
        if client_id:
            del self.active_connections[client_id]
            if client_id in self.logged_in_players:
                del self.logged_in_players[client_id]
            logger.info(f"Client {client_id} disconnected")

    def get_client_id(self, websocket: WebSocket) -> str:
        for client_id, ws in self.active_connections.items():
            if ws == websocket:
                return client_id
        return None

    def _parse_command(self, message: str) -> tuple[str, str]:
        """Split message into command and args"""
        parts = message.strip().split(maxsplit=1)
        command = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        return command, args

    async def handle_message(self, websocket: WebSocket, message: str):
        client_id = self.get_client_id(websocket)
        if not client_id:
            logger.error("Client not found in active connections")
            return WebSocketMessage(type='error', message='Connection error')

        # Parse command and args
        command_name, args = self._parse_command(message)
        command_class = self.command_registry.get_command(command_name)

        if not command_class:
            logger.error(f"Unknown command: {command_name}")
            return WebSocketMessage(
                type='error',
                message=f'Unknown command. Type "help" for available commands.'
            )

        # Create command instance and execute
        try:
            command = command_class()
            return await command.execute(args)
        except Exception as e:
            logger.error(f"Command execution error: {str(e)}")
            return WebSocketMessage(type='error', message='Error executing command')