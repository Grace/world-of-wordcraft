import sqlite3
import os
import json

DB_FILE = "game.db"

def init_db():
    """Initialize the database and create tables if they do not exist."""
    if not os.path.exists(DB_FILE):
        print("Database file not found. Creating a new one...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create players table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id TEXT PRIMARY KEY,
        name TEXT,
        location_x INTEGER,
        location_y INTEGER,
        location_z INTEGER,
        inventory TEXT
    )
    """)

    # Create rooms table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        coordinates TEXT PRIMARY KEY,
        description TEXT,
        exits TEXT,
        puzzle TEXT,
        npc TEXT,
        items TEXT
    )
    """)

    conn.commit()
    conn.close()

def get_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_FILE)

def save_room(coordinates, room_data):
    """Save a room to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO rooms (coordinates, description, exits, puzzle, npc, items)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        json.dumps(coordinates),
        room_data["description"],
        json.dumps(room_data["exits"]),
        room_data.get("puzzle"),
        json.dumps(room_data.get("npc", [])),
        json.dumps(room_data.get("items", []))
    ))
    conn.commit()
    conn.close()

def get_room(coordinates):
    """Retrieve a room from the database by its coordinates."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT description, exits, puzzle, npc, items FROM rooms WHERE coordinates = ?", (json.dumps(coordinates),))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "description": result[0],
            "exits": json.loads(result[1]),
            "puzzle": result[2],
            "npc": json.loads(result[3]),
            "items": json.loads(result[4]),
        }
    return None

def save_player(player_id, player_data):
    """Save a player's data to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO players (id, name, location_x, location_y, location_z, inventory)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        player_id,
        player_data["name"],
        player_data["location"][0],
        player_data["location"][1],
        player_data["location"][2],
        json.dumps(player_data.get("inventory", []))
    ))
    conn.commit()
    conn.close()

def load_player(player_id):
    """Load a player's data from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, location_x, location_y, location_z, inventory
        FROM players
        WHERE id = ?
    """, (player_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "id": player_id,
            "name": result[0],
            "location": (result[1], result[2], result[3]),
            "inventory": json.loads(result[4]),
        }
    return None

def get_players_in_room(location, exclude=None):
    """
    Get a list of players in a specific room.

    Args:
        location (tuple): The (x, y, z) coordinates of the room.
        exclude (str): The player ID to exclude from the results.

    Returns:
        list: A list of player names in the room.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM players
        WHERE location_x = ? AND location_y = ? AND location_z = ?
    """, location)
    players = cursor.fetchall()
    conn.close()

    return [player[0] for player in players if player[0] != exclude]

def update_player_location(player_id, location):
    """
    Update a player's location in the database.

    Args:
        player_id (str): The unique ID of the player.
        location (tuple): The new (x, y, z) coordinates of the player.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE players
        SET location_x = ?, location_y = ?, location_z = ?
        WHERE id = ?
    """, (*location, player_id))
    conn.commit()
    conn.close()
