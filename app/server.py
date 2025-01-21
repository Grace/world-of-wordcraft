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
from datetime import datetime, timedelta
import re
from typing import Dict
from collections import defaultdict
import html
import os
from dotenv import load_dotenv
import jwt

load_dotenv()

# Base directory for static files
WEB_DIR = Path(__file__).parent.parent / "web"

# FastAPI app for serving static files and WebSocket handling
fastapi_app = FastAPI()

# Allow CORS for all origins (adjust for production)
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production (e.g., ["https://your-domain.com"])
    allow_credentials=True,
    allow_methods=["*"],
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
        "exp": datetime.utcnow() + TOKEN_EXPIRY
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> str:
    """Verify JWT token and return player_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.InvalidTokenError:
        return None

@fastapi_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    player = None
    client_id = f"{websocket.client.host}:{websocket.client.port}"
    
    try:
        # Initial auth request
        await websocket.send_json({
            "type": "auth_request",
            "message": "Enter 'login <name> <password>' or 'register <name> <password>'.\nAvailable commands:\n- highcontrast on/off\n- fontsize <number>"
        })
        
        while True:
            try:
                message = await websocket.receive_text()
                
                # Rate limiting check
                if not check_rate_limit(client_id):
                    await websocket.send_json({
                        "type": "error",
                        "message": "Too many requests. Please slow down."
                    })
                    await websocket.close(code=1008, reason="Rate limit exceeded")
                    return
                    
                # Input validation
                message = sanitize_input(message)
                if not message:
                    continue
                    
                # Command validation
                command = message.split()[0].lower()
                if command not in ALLOWED_COMMANDS:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid command."
                    })
                    continue
                
                # Handle pre-auth commands
                if message.startswith("highcontrast "):
                    setting = message.split(" ")[1].lower()
                    if setting in ["on", "off"]:
                        await websocket.send_json({
                            "type": "theme",
                            "theme": "high-contrast" if setting == "on" else "default",
                            "message": f"High contrast mode turned {setting}."
                        })
                    continue
                elif message.startswith("fontsize "):
                    try:
                        size = int(message.split(" ")[1])
                        await websocket.send_json({
                            "type": "fontsize",
                            "size": size,
                            "message": f"Font size set to {size}px."
                        })
                        continue
                    except (IndexError, ValueError):
                        await websocket.send_json({
                            "type": "error",
                            "message": "Usage: fontsize <number>"
                        })
                        continue
                    
                # Handle auth flow
                if not player:
                    parts = message.split()
                    if len(parts) < 3:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Invalid format. Use: login/register <name> <password>"
                        })
                        continue

                    command, name, password = parts[0], parts[1], parts[2]
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    
                    if command == "register":
                        player_id, message = create_player(name, password_hash)
                        if player_id:
                            player = load_player(player_id)
                            # Only send one success message
                            await websocket.send_json({
                                "type": "auth_success",
                                "message": "Account created successfully. Welcome to World of Wordcraft!\n\nType 'look' to see where you are."
                            })
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "message": message
                            })
                            
                    elif command == "login":
                        player_id, message = verify_player(name, password_hash)
                        if player_id:
                            player = load_player(player_id)
                            await websocket.send_json({
                                "type": "auth_success",
                                "message": f"Welcome back, {player['name_original']}!\n\nType 'look' to see where you are."
                            })
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "message": message
                            })
                    
                    if not player:
                        continue

                    # Check ban status after login/register
                    if player:
                        ban_reason = is_banned(player["id"])
                        if ban_reason:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"You are banned. Reason: {ban_reason}"
                            })
                            await websocket.close(code=1008, reason="Banned")
                            return

                    # Add to connected clients
                    connected_clients[player_id] = websocket

                # Handle normal game commands
                else:
                    try:
                        response = game_logic.handle_action(player, message)
                        
                        # Handle special responses
                        if isinstance(response, dict):
                            if response["type"] == "logout":
                                await websocket.send_json({
                                    "type": "game_message",
                                    "message": response["message"]
                                })
                                if player["id"] in connected_clients:
                                    del connected_clients[player["id"]]
                                await websocket.close()
                                return
                            if response["type"] == "kick":
                                target_websocket = connected_clients.get(response["target_id"])
                                if target_websocket:
                                    await target_websocket.send_json({
                                        "type": "error",
                                        "message": f"You have been kicked by {player['name_original']}"
                                    })
                                    await target_websocket.close(code=1000, reason="Kicked by moderator")
                                await websocket.send_json({
                                    "type": "game_message",
                                    "message": response["message"]
                                })
                                continue
                            # Handle ban response
                            if isinstance(response, dict) and response["type"] == "ban":
                                target_websocket = connected_clients.get(response["target_id"])
                                if target_websocket:
                                    await target_websocket.send_json({
                                        "type": "error",
                                        "message": response["player_message"]
                                    })
                                    await target_websocket.close(code=1008, reason="Banned")
                                await websocket.send_json({
                                    "type": "game_message",
                                    "message": response["admin_message"]
                                })
                                continue
                        
                        # Normal message handling
                        await websocket.send_json({
                            "type": "game_message",
                            "message": response
                        })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "message": str(e)
                        })

            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Error handling message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "An error occurred processing your request"
                })
                
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
    except Exception as e:
        print(f"Error in websocket connection: {e}")
    finally:
        if player and player["id"] in connected_clients:
            del connected_clients[player["id"]]
        print(f"Connection closed for client {client_id}")

if __name__ == "__main__":
    import uvicorn

    # Initialize the database
    init_db()

    print("Starting server on http://0.0.0.0:5001")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5001)
