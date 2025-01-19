from flask import Flask, send_from_directory
from flask_cors import CORS
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.wsgi import WSGIMiddleware
import json
from app.database import load_player, save_player
from app.game_logic import handle_action

# Flask app for serving the web client
flask_app = Flask(__name__)
CORS(flask_app)

@flask_app.route('/')
def index():
    """Serve the main HTML file."""
    return send_from_directory('../web', 'index.html')

@flask_app.route('/<path:filename>')
def static_files(filename):
    """Serve static files like CSS and JavaScript."""
    return send_from_directory('../web', filename)

# FastAPI app for WebSocket handling
fastapi_app = FastAPI()

# Mount Flask for HTTP routes
fastapi_app.mount("/flask", WSGIMiddleware(flask_app))

# Dictionary to store WebSocket connections
connected_clients = {}

@fastapi_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for gameplay."""
    await websocket.accept()
    origin = websocket.headers.get("origin", "Unknown")
    print(f"WebSocket connection attempted from origin: {origin}")
    
    try:
        # Request player name
        await websocket.send_json({"message": "Enter your name:"})
        player_name = await websocket.receive_text()
        print(f"Player name received: {player_name}")

        # Create or load player data
        player_id = websocket.client.host
        player = load_player(player_id) or {
            "id": player_id,
            "name": player_name,
            "location": (0, 0, 0),
            "inventory": [],
        }
        save_player(player_id, player)

        # Add WebSocket to connected clients
        connected_clients[player_id] = websocket

        # Welcome the player
        await websocket.send_json({"message": f"Welcome {player_name}! Type 'look' to start."})

        # Main gameplay loop
        while True:
            try:
                command = await websocket.receive_text()
                print(f"Command received: {command}")  # Log the command for debugging
                if command:
                    response = handle_action(player, command)
                    await websocket.send_json({"message": response})
            except WebSocketDisconnect:
                print(f"WebSocket disconnected: {player_id}")
                break

    except Exception as e:
        print(f"WebSocket error: {e}")

    finally:
        # Clean up on disconnect
        if player_id in connected_clients:
            del connected_clients[player_id]
            print(f"Client {player_id} disconnected.")
        print("WebSocket connection closed.")

if __name__ == "__main__":
    import uvicorn
    print("Starting server with Flask and WebSocket support on http://0.0.0.0:5001")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5001)
