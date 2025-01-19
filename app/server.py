from flask import Flask, send_from_directory
import threading
import asyncio
import websockets
import json
from app.database import init_db, save_player, load_player
from app.game_logic import handle_action
from waitress import serve

# Flask app for serving the web client
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    """Serve the main HTML file."""
    return send_from_directory('../web', 'index.html')

@flask_app.route('/<path:filename>')
def static_files(filename):
    """Serve static files like CSS and JavaScript."""
    return send_from_directory('../web', filename)

# WebSocket server for the game
connected_clients = {}

async def websocket_handler(websocket, path):
    """Handle WebSocket connections."""
    try:
        await websocket.send(json.dumps({"message": "Enter your name:"}))
        player_name = await websocket.recv()
        player_id = str(websocket.remote_address)
        player = load_player(player_id) or {
            "id": player_id,
            "name": player_name,
            "location": (0, 0, 0),
            "inventory": []
        }
        save_player(player_id, player)
        connected_clients[player_id] = websocket

        await websocket.send(json.dumps({"message": f"Welcome {player_name}! Type 'look' to start."}))

        while True:
            command = await websocket.recv()
            print(f"Command received: {command}")  # Log the command for debugging
            response = handle_action(player, command)
            await websocket.send(json.dumps({"message": response}))
    except websockets.exceptions.ConnectionClosed:
        print("A client disconnected.")
    finally:
        connected_clients.pop(player_id, None)

# Run Flask and WebSocket server concurrently
def run_flask():
    """Run the Flask app using Waitress."""
    print("Starting Flask server with Waitress on http://0.0.0.0:5001")
    serve(flask_app, host="0.0.0.0", port=5001)

async def run_websocket():
    """Run the WebSocket server."""
    print("Starting WebSocket server on ws://0.0.0.0:8765")
    init_db()  # Ensure the database is initialized
    server = await websockets.serve(websocket_handler, "0.0.0.0", 8765)
    await server.wait_closed()

if __name__ == "__main__":
    # Start Flask server in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Start WebSocket server in the main event loop
    asyncio.run(run_websocket())
