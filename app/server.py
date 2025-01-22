import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import APIKeyCookie
from pathlib import Path
from app.database import (
    init_db, 
    load_player, 
    save_player, 
    create_player, 
    verify_player,
    is_banned
)
from app.game_logic import GameLogic
import hashlib
from datetime import datetime, timedelta, timezone
import re
from typing import Dict
from collections import defaultdict
import html
import os
from dotenv import load_dotenv
import jwt
import json
from starlette.websockets import WebSocketState

load_dotenv()

# Base directory for static files
WEB_DIR = Path(__file__).parent.parent / "web"

# FastAPI app for serving static files and WebSocket handling
fastapi_app = FastAPI()

# Get environment
ENV = os.getenv('ENVIRONMENT', 'development')

# Set allowed origins based on environment
ALLOWED_ORIGINS = (
    ["http://localhost:5001"] if ENV == 'development'
    else ["https://world-of-wordcraft.up.railway.app"]
)

# CORS middleware configuration
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Serve the main HTML file at the root endpoint
@fastapi_app.get("/")
async def index():
    """Serve the main HTML file."""
    return FileResponse(WEB_DIR / "index.html")

# Serve static files like JavaScript and CSS
@fastapi_app.get("/{filename}")
async def static_files(filename: str):
    """Serve static files from the web directory."""
    file_path = WEB_DIR / filename
    if (file_path.exists()):
        return FileResponse(file_path)
    return {"error": "File not found"}, 404

# WebSocket connections
connected_clients = {}

# Create game logic instance
game_logic = GameLogic(connected_clients)

# Rate limiting settings
RATE_LIMIT = 5  # messages per second
RATE_WINDOW = 1  # seconds
MESSAGE_SIZE_LIMIT = 1000  # characters

# Security settings
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
TOKEN_EXPIRY = timedelta(hours=24)
ALLOWED_COMMANDS = {
    "look", "go", "take", "inventory", "logout", "highcontrast", "fontsize",
    "interact", "use", "solve", "register", "login", "l", "i"
}

# Add to ALLOWED_COMMANDS
ALLOWED_COMMANDS.update({
    "grant_role", "kick", "mute", "ban", "edit",
    "spawn_item", "teleport"
})

# Add to ALLOWED_COMMANDS
ALLOWED_COMMANDS.update({
    "say", "yell", "tell"
})

# Add to ALLOWED_COMMANDS
ALLOWED_COMMANDS.update({
    "inspect"
})

# Add to ALLOWED_COMMANDS
ALLOWED_COMMANDS.update({
    "speech"
})

# Update help message
REGISTER_OR_LOGIN_MESSAGE = """Welcome to World of Wordcraft!


Enter 'login <name> <password>' or 'register <name> <password>'.

Type 'help <command>' for more info on a specific command.


Available accessibility commands:
- highcontrast on/off
- fontsize <number>
- speech on/off
- speech rate <0.1-10>
- speech repeat"""

# Rate limiting storage
rate_limits: Dict[str, list] = defaultdict(list)

def sanitize_input(message: str) -> str:
    """Sanitize user input"""
    # Remove any non-alphanumeric chars except spaces and common punctuation
    sanitized = re.sub(r'[^a-zA-Z0-9\s\-_.,!?]', '', message)
    # Escape HTML
    sanitized = html.escape(sanitized)
    return sanitized[:MESSAGE_SIZE_LIMIT]

def check_rate_limit(client_id: str) -> bool:
    """Check if client has exceeded rate limit"""
    now = datetime.now()
    # Clean up old timestamps
    rate_limits[client_id] = [t for t in rate_limits[client_id] 
                             if (now - t).total_seconds() < RATE_WINDOW]
    
    if len(rate_limits[client_id]) >= RATE_LIMIT:
        return False
        
    rate_limits[client_id].append(now)
    return True

def create_token(player_id: str) -> str:
    """Create JWT token for authenticated player"""
    payload = {
        "sub": player_id,
        "exp": datetime.now(timezone.utc) + TOKEN_EXPIRY
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> str:
    """Verify JWT token and return player_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.InvalidTokenError:
        return None

# Process authenticated player commands
async def process_player_command(player, data, websocket):
    try:
        # Get command content from either format
        command = data.get("content") if isinstance(data, dict) else data
        sanitized = sanitize_input(command)
        
        print(f"Debug: Processing command '{sanitized}' for {player['name_original']}")
        
        # Handle empty commands
        if not sanitized:
            await websocket.send_json({
                "type": "message",
                "message": "Please enter a command"
            })
            return
            
        # Process command through game logic
        result = game_logic.handle_action(player, sanitized)
        
        # Ensure result is JSON serializable
        if not isinstance(result, dict):
            result = {
                "type": "message",
                "message": str(result)
            }
            
        print(f"Debug: Command result: {result}")
        await websocket.send_json(result)
        
    except Exception as e:
        print(f"Error processing command: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": "Error processing command"
        })

async def handle_banned_player(player_id: str, websocket: WebSocket):
    """Handle a banned player"""
    await websocket.send_json({
        "type": "error",
        "message": "Account is banned"
    })
    await websocket.close()

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.player_connections: Dict[str, str] = {}  # player_id -> client_id

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    async def disconnect(self, client_id: str, player_id: str = None):
        if client_id in self.active_connections:
            ws = self.active_connections[client_id]
            if ws.application_state != WebSocketState.DISCONNECTED:
                await ws.close()
            del self.active_connections[client_id]
        if player_id:
            if player_id in connected_clients:
                del connected_clients[player_id]
            if player_id in self.player_connections:
                del self.player_connections[player_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except WebSocketDisconnect:
                await self.disconnect(client_id)

manager = ConnectionManager()

async def send_login_or_register_message(websocket: WebSocket):
    """Send login or register message to client"""
    message = {
        "type": "message",
        "message": REGISTER_OR_LOGIN_MESSAGE
    }
    websocket.send_json(message)

@fastapi_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = f"{websocket.client.host}:{websocket.client.port}"
    player = None
    
    try:
        await manager.connect(websocket, client_id)
        
        # Send initial welcome message
        send_login_or_register_message(websocket)
        
        while True:
            try:
                raw_message = await websocket.receive_text()
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                data = {"type": "command", "content": raw_message}
            except WebSocketDisconnect:
                await manager.disconnect(client_id, player["id"] if player else None)
                break
                
            try:
                if data.get("type") == "token_auth":
                    player_id = verify_token(data.get("token"))
                    if player_id:
                        player = load_player(player_id)
                        if player:
                            manager.player_connections[player["id"]] = client_id
                            connected_clients[player["id"]] = websocket
                            await manager.send_message(client_id, {
                                "type": "auth_success",
                                "token": create_token(player["id"]),
                                "message": f"Welcome back, {player['name_original']}! Type 'look' to see where you are."
                            })
                            continue
                
                if player:
                    await process_player_command(player, data, websocket)
                    continue
                    
                await handle_auth_command(data, websocket)
                
            except Exception as e:
                print(f"Error processing message: {str(e)}")
                continue
                
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        
    finally:
        await manager.disconnect(client_id, player["id"] if player else None)

if __name__ == "__main__":
    import uvicorn

    # Initialize the database
    init_db()

    print("Starting server on http://0.0.0.0:5001")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5001)
