from flask import Flask, send_from_directory
from flask_cors import CORS
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
from app.database import load_player, save_player
from app.game_logic import handle_action

# FastAPI app for WebSocket handling
fastapi_app = FastAPI()

# Allow CORS for all origins (adjust for production if needed)
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flask app for serving the web client
flask_app = Flask(__name__)
CORS(flask_app)

@flask_app.route("/")
def index():
    """Serve the main HTML file."""
    return send_from_directory("../web", "index.html")

@flask_app.route("/<path:filename>")
def static_files(filename):
    """Serve static files like CSS and JavaScript."""
    return send_from_directory("../web", filename)

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
    import threading
    from waitress import serve

    def run_flask():
        """Run the Flask app using Waitress."""
        print("Starting Flask server...")
        serve(flask_app, host="0.0.0.0", port=5000)

    # Run Flask in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Run FastAPI WebSocket server on a different port
    print("Starting FastAPI server for WebSocket...")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5001)
