from starlette.websockets import WebSocketState
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

class ConnectionManager:

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.player_connections: Dict[str, str] = {}  # player_id -> client_id
        self.connected_clients: Dict[str, WebSocket] = {}  # player_id -> websocket

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def add_connected_client(self, player_id: str, websocket: WebSocket):
        self.connected_clients[player_id] = websocket

    def add_connected_player(self, player_id: str):
        self.player_connections[player_id] = player_id

    async def disconnect(self, client_id: str, player_id: str = None):
        if client_id in self.active_connections:
            ws = self.active_connections[client_id]
            if ws.application_state != WebSocketState.DISCONNECTED:
                await ws.close()
            del self.active_connections[client_id]
        if player_id:
            if player_id in self.connected_clients:
                del self.connected_clients[player_id]
            if player_id in self.player_connections:
                del self.player_connections[player_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except WebSocketDisconnect:
                await self.disconnect(client_id)

manager = ConnectionManager()