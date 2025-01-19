import sqlite3
import os

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
        INSERT OR REPLACE INTO rooms (coordinates, data) VALUES (?, ?)
    """, (json.dumps(coordinates), json.dumps(room_data)))
    conn.commit()
    conn.close()

def get_room(coordinates):
    """
    Retrieve a room from the database by its coordinates.

    Args:
        coordinates (tuple): The (x, y, z) coordinates of the room.

    Returns:
        dict: The room data if found, or None if the room does not exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM rooms WHERE coordinates = ?", (json.dumps(coordinates),))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else None

def save_player(player_id, player_data):
    """Save a player's data to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO players (id, data) VALUES (?, ?)
    """, (player_id, json.dumps(player_data)))
    conn.commit()
    conn.close()

def load_player(player_id):
    """Load a player's data from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM players WHERE id = ?", (player_id,))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else None

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
    cursor.execute("SELECT data FROM players")
    players = cursor.fetchall()
    conn.close()

    players_in_room = []
    for player_data in players:
        player = json.loads(player_data[0])
        if tuple(player["location"]) == tuple(location) and player["id"] != exclude:
            players_in_room.append(player["name"])
    return players_in_room

def update_player_location(player_id, location):
    """
    Update a player's location in the database.

    Args:
        player_id (str): The unique ID of the player.
        location (tuple): The new (x, y, z) coordinates of the player.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM players WHERE id = ?", (player_id,))
    result = cursor.fetchone()
    if result:
        player = json.loads(result[0])
        player["location"] = location
        cursor.execute("""
            INSERT OR REPLACE INTO players (id, data) VALUES (?, ?)
        """, (player_id, json.dumps(player)))
    conn.commit()
    conn.close()
