from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from app.database import init_db, load_player, save_player, update_player_location, get_players_in_room, create_player, verify_player
from app.game_logic import game_logic 
import hashlib

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

@fastapi_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    player = None
    
    try:
        # Auth request
        await websocket.send_json({
            "type": "auth_request",
            "message": "Enter 'login <name> <password>' or 'register <name> <password>'"
        })
        
        # Handle login/register
        auth_message = await websocket.receive_text()
        parts = auth_message.split()
        
        if len(parts) < 3:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid format. Use: login/register <name> <password>"
            })
            return

        command, name, password = parts[0], parts[1], parts[2]
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if command == "register":
            player_id, message = create_player(name, password_hash)
            await websocket.send_json({
                "type": "auth_success" if player_id else "error",
                "message": message
            })
            if player_id:
                player = load_player(player_id)
                # Send welcome message after successful registration
                await websocket.send_json({
                    "type": "game_message",
                    "message": f"Welcome, {name}! You have joined World of Wordcraft. Type 'look' to begin your adventure."
                })
                
        elif command == "login":
            player_id, message = verify_player(name, password_hash)
            await websocket.send_json({
                "type": "auth_success" if player_id else "error",
                "message": message
            })
            if player_id:
                player = load_player(player_id)
                # Send welcome message after successful login with proper name casing
                await websocket.send_json({
                    "type": "game_message",
                    "message": f"Welcome back, {player['name_original']}! Type 'look' to see where you are."
                })
        
        if not player:
            return

        # Add to connected clients
        connected_clients[player_id] = websocket

        # Game loop
        while True:
            command = await websocket.receive_text()
            if command:
                try:
                    response = game_logic.handle_action(player, command)
                    
                    # Handle theme changes
                    if isinstance(response, dict) and response["type"] == "theme":
                        await websocket.send_json(response)
                    # Handle logout command
                    elif isinstance(response, dict) and response["type"] == "logout":
                        try:
                            save_player(player['id'], player)
                            del connected_clients[player['id']]
                            await websocket.send_json({
                                "type": "game_message",
                                "message": response["message"]
                            })
                            await websocket.close()
                            return
                        except Exception as e:
                            await websocket.send_json({
                                "type": "error",
                                "message": "Error during logout. Please try again."
                            })
                    
                    # Normal message handling
                    else:
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
        if player:
            del connected_clients[player['id']]
        print(f"Client {player['id'] if player else 'unknown'} disconnected")
    finally:
        if player:
            save_player(player['id'], player)

if __name__ == "__main__":
    import uvicorn

    # Initialize the database
    init_db()

    print("Starting server on http://0.0.0.0:5001")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5001)
