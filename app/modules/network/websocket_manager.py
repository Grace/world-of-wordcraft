from fastapi import WebSocket
from typing import Dict, Set
import logging
from .websocket_message import WebSocketMessage
from ..commands.command_registry import CommandRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WELCOME_MESSAGE = """Welcome to World of Wordcraft!
Enter 'login <name> <password>' or 'register <name> <password>'.

Type 'help <command>' for more info on a specific command.

Available accessibility commands:
- highcontrast on/off
- fontsize <number>
- speech on/off
- speech rate <0.1-10>
- speech repeat"""

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.command_registry = CommandRegistry()

    async def connect(self, websocket: WebSocket) -> str:
        await websocket.accept()
        self.active_connections.add(websocket)
        client_id = f"{websocket.client.host}:{websocket.client.port}"
        
        # Send welcome message
        welcome = WebSocketMessage(type='welcome', message=WELCOME_MESSAGE)
        await websocket.send_json(welcome.to_dict())
        
        logger.info(f"Client {client_id} connected")
        return client_id

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        client_id = f"{websocket.client.host}:{websocket.client.port}"
        logger.info(f"Client {client_id} disconnected")

    async def handle_message(self, websocket: WebSocket, message: str):
        try:
            # Split into command and args
            parts = message.strip().split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            sanitized_command = self.command_registry.sanitize_command(command)
            
            if self.command_registry.is_valid_command(sanitized_command):
                command_instance = self.command_registry.commands[sanitized_command]()
                return await command_instance.execute(args)
            else:
                return WebSocketMessage(
                    type='error',
                    message=f"Unknown command: {command}"
                )
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return WebSocketMessage(type='error', message=str(e))