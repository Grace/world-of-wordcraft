from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from app.database import load_player, save_player, update_player_location, get_players_in_room
from app.game_logic import handle_action, get_room, get_players_in_room, generate_room_description

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
    if file_path.exists():
        return FileResponse(file_path)
    return {"error": "File not found"}, 404

# WebSocket connections
connected_clients = {}

@fastapi_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for gameplay."""
    await websocket.accept()
    origin = websocket.headers.get("origin", "Unknown")
    print(f"WebSocket connection attempted from origin: {origin}")

    player_id = websocket.client.host
    player_room = None  # Track the player's current room

    try:
        # Request player name
        await websocket.send_json({"message": "Enter your name:"})
        player_name = await websocket.receive_text()
        print(f"Player name received: {player_name}")

        # Create or load player data
        player = load_player(player_id) or {
            "id": player_id,
            "name": player_name,
            "location": (0, 0, 0),
            "inventory": [],
        }
        save_player(player_id, player)

        # Add WebSocket to connected clients
        connected_clients[player_id] = websocket
        player_room = player["location"]

        # Welcome the player
        await websocket.send_json({"message": f"Welcome {player_name}! Type 'look' to start."})

        # Main gameplay loop
        while True:
            command = await websocket.receive_text()
            print(f"Command received: {command}")
            if command:
                response = handle_action(player, command)
                player_room = player["location"]  # Update player's current room
                save_player(player_id, player)
                await websocket.send_json({"message": response})

    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {player_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")

    finally:
        # Clean up on disconnect
        if player_id in connected_clients:
            del connected_clients[player_id]
            print(f"Client {player_id} disconnected.")
        
        # Remove player from their room
        if player_room:
            players_in_room = get_players_in_room(player_room)
            if player_id in players_in_room:
                players_in_room.remove(player_id)
                update_player_location(player_room, players_in_room)

        print("WebSocket connection closed.")

if __name__ == "__main__":
    import uvicorn

    print("Starting server on http://0.0.0.0:5001")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5001)
