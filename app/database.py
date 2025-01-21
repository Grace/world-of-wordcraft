import sqlite3
import os
import json

DB_FILE = "game.db"

def init_db():
    """Initialize database schema"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    with open('app/schema.sql') as f:
        cursor.executescript(f.read())
    
    conn.commit()
    conn.close()

def get_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_FILE)

def save_room(coordinates, room_data):
    """Save a room to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO rooms (coordinates, description, exits, npcs, items, puzzles)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            json.dumps(coordinates),
            room_data["description"],
            json.dumps(room_data["exits"]),
            json.dumps(room_data.get("npcs", [])),
            json.dumps(room_data.get("items", [])),
            json.dumps(room_data.get("puzzles", []))
        ))
        conn.commit()
    finally:
        conn.close()

def get_room(coordinates):
    """Retrieve a room from the database by its coordinates."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT description, exits, puzzles, npcs, items FROM rooms WHERE coordinates = ?", (json.dumps(coordinates),))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "description": result[0],
            "exits": json.loads(result[1]),
            "puzzles": result[2],
            "npcs": json.loads(result[3]),
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
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT name_original, location_x, location_y, location_z, inventory 
            FROM players WHERE id = ?
        """, (player_id,))
        result = cursor.fetchone()
        
        if result:
            name_original, x, y, z, inventory = result
            return {
                "id": player_id,
                "name": name_original.lower(),
                "name_original": name_original,
                "location": (x, y, z),
                "inventory": json.loads(inventory)
            }
        return None
    finally:
        conn.close()

def get_players_in_room(location, exclude=None):
    """Get players in room excluding current player."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        x, y, z = location
        cursor.execute("""
            SELECT name_original 
            FROM players 
            WHERE location_x = ? 
            AND location_y = ? 
            AND location_z = ? 
            AND id != ?
        """, (x, y, z, exclude))
        
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

def update_player_location(player_id, location):
    """
    Update a player's location in the database.

    Args:
        player_id (str): The unique ID of the player.
        location (tuple): The new (x, y, z) coordinates of the player.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        x, y, z = location
        cursor.execute("""
            UPDATE players 
            SET location_x = ?, location_y = ?, location_z = ?
            WHERE id = ?
        """, (x, y, z, player_id))
        conn.commit()
    finally:
        conn.close()

def create_player(name, password_hash):
    """Create a new player account with case-insensitive name."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if player exists (case-insensitive)
        cursor.execute("SELECT id FROM players WHERE name = ? COLLATE NOCASE", (name,))
        if cursor.fetchone():
            return None, "Player name already exists"
            
        player_id = f"player_{name.lower()}"
        try:
            cursor.execute("""
                INSERT INTO players (id, name, name_original, password_hash, location_x, location_y, location_z, inventory)
                VALUES (?, ?, ?, ?, 0, 0, 0, '[]')
            """, (player_id, name.lower(), name, password_hash))
            conn.commit()
            return player_id, "Account created successfully"
        except sqlite3.IntegrityError:
            return None, "Player name already exists"
    finally:
        conn.close()

def verify_player(name, password_hash):
    """Verify player credentials with case-insensitive name."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, password_hash FROM players 
            WHERE name = ? COLLATE NOCASE
        """, (name,))
        result = cursor.fetchone()
        
        if not result:
            return None, "Player not found"
        if result[1] != password_hash:
            return None, "Invalid password"
        return result[0], "Login successful"
    finally:
        conn.close()
