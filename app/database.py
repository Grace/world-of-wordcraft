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
    """Get room data with proper JSON parsing."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT description, exits, npcs, items, puzzles 
            FROM rooms 
            WHERE coordinates = ?
        """, (f"{coordinates[0]},{coordinates[1]},{coordinates[2]}",))
        
        result = cursor.fetchone()
        if result:
            description, exits, npcs, items, puzzles = result
            return {
                "description": description,
                "exits": json.loads(exits),
                "npcs": json.loads(npcs),
                "items": json.loads(items),
                "puzzles": json.loads(puzzles)
            }
        return None
    finally:
        conn.close()

def save_player(player_id, player_data):
    """Save player state to database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE players 
            SET name = ?,
                name_original = ?,
                location_x = ?,
                location_y = ?,
                location_z = ?,
                inventory = ?
            WHERE id = ?
        """, (
            player_data["name"].lower(),
            player_data["name_original"],
            player_data["location"][0],
            player_data["location"][1],
            player_data["location"][2],
            json.dumps(player_data.get("inventory", [])),
            player_id
        ))
        conn.commit()
    finally:
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
            return player_id, None
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
        return result[0], None 
    finally:
        conn.close()

def get_player_role(player_id):
    """Get player's role and permissions."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT r.id, r.permissions
            FROM players p
            JOIN roles r ON p.role_id = r.id
            WHERE p.id = ?
        """, (player_id,))
        result = cursor.fetchone()
        if result:
            return {
                "role": result[0],
                "permissions": json.loads(result[1])
            }
        return None
    finally:
        conn.close()

def check_permission(player_id, permission):
    """Check if player has permission."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT r.permissions
            FROM players p
            JOIN roles r ON p.role_id = r.id
            WHERE p.id = ?
        """, (player_id,))
        result = cursor.fetchone()
        
        if result:
            permissions = json.loads(result[0])
            print(f"Debug - Player: {player_id}, Command: {permission}, Permissions: {permissions}")  # Debug line
            return permission in permissions
        return False
    finally:
        conn.close()

def grant_role(player_id, role_id, granter_id):
    """Grant role to player (requires admin)."""
    if not check_permission(granter_id, "grant_role"):
        return False, "Insufficient permissions"
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE players 
            SET role_id = ?
            WHERE id = ?
        """, (role_id, player_id))
        conn.commit()
        return True, "Role granted successfully"
    finally:
        conn.close()

def ban_player(target_id, banner_id, reason=None):
    """Ban a player."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO banned_players (player_id, banned_by, reason)
            VALUES (?, ?, ?)
        """, (target_id, banner_id, reason))
        conn.commit()
        return True
    finally:
        conn.close()

def is_banned(player_id):
    """Check if player is banned."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT reason FROM banned_players WHERE player_id = ?", (player_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()
