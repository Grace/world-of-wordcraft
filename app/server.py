from flask import Flask, send_from_directory, request
from flask_sockets import Sockets
import threading
import asyncio
import json
from app.database import init_db, save_player, load_player
from app.game_logic import handle_action
from waitress import serve
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

# Flask app for serving the web client
flask_app = Flask(__name__)
sockets = Sockets(flask_app)  # Add WebSocket support to Flask

# Dictionary to store connected WebSocket clients
connected_clients = {}


@flask_app.route('/')
def index():
    """Serve the main HTML file."""
    return send_from_directory('../web', 'index.html')


@flask_app.route('/<path:filename>')
def static_files(filename):
    """Serve static files like CSS and JavaScript."""
    return send_from_directory('../web', filename)


@sockets.route('/ws')
def websocket_handler(ws):
    """Handle WebSocket connections."""
    try:
        ws.send(json.dumps({"message": "Enter your name:"}))
        player_name = ws.receive()
        player_id = str(request.remote_addr)
        player = load_player(player_id) or {
            "id": player_id,
            "name": player_name,
            "location": (0, 0, 0),
            "inventory": [],
        }
        save_player(player_id, player)
        connected_clients[player_id] = ws

        ws.send(json.dumps({"message": f"Welcome {player_name}! Type 'look' to start."}))

        while not ws.closed:
            command = ws.receive()
            print(f"Command received: {command}")  # Log the command for debugging
            if command:
                response = handle_action(player, command)
                ws.send(json.dumps({"message": response}))

    except Exception as e:
        print(f"WebSocket error: {e}")

    finally:
        if player_id in connected_clients:
            del connected_clients[player_id]
            print(f"Client {player_id} disconnected.")


def run_server():
    """Run the Flask app with WebSocket support using gevent."""
    init_db()
    print("Starting server with WebSocket support on http://0.0.0.0:5001")
    server = pywsgi.WSGIServer(("0.0.0.0", 5001), flask_app, handler_class=WebSocketHandler)
    server.serve_forever()


if __name__ == "__main__":
    run_server()
