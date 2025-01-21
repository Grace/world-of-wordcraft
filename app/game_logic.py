from dotenv import load_dotenv
import os
from .modules.room_generator import RoomGenerator
from .modules.action_handler import ActionHandler
from .modules.game_state import GameState

load_dotenv()

class GameLogic:
    def __init__(self):
        self.room_generator = RoomGenerator(os.getenv('OPENAI_API_KEY'))
        self.action_handler = ActionHandler()
        self.game_state = GameState()

    def handle_action(self, player, action):
        """Handle a player's action and return the result."""
        location = player["location"]
        room = self.game_state.get_room(location)
        
        if not room:
            room = self.room_generator.generate_room(location)
            self.game_state.save_room(location, room)

        return self.action_handler.handle(player, action, room)

    def generate_room_description(self, coordinates):
        """Generate a new room at the given coordinates."""
        return self.room_generator.generate_room(coordinates)
    
    def create_player(name, password_hash):
        """Create a new player account."""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if player exists
        cursor.execute("SELECT id FROM players WHERE name = ?", (name,))
        if cursor.fetchone():
            conn.close()
            return None, "Player name already exists"
            
        player_id = f"player_{name.lower()}"
        cursor.execute("""
            INSERT INTO players (id, name, password_hash, location_x, location_y, location_z, inventory)
            VALUES (?, ?, ?, 0, 0, 0, '[]')
        """, (player_id, name, password_hash))
        
        conn.commit()
        conn.close()
        return player_id, "Account created successfully"

    def verify_player(name, password_hash):
        """Verify player credentials."""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, password_hash FROM players 
            WHERE name = ?
        """, (name,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None, "Player not found"
        if result[1] != password_hash:
            return None, "Invalid password"
        return result[0], "Login successful"

# Create singleton instance
game_logic = GameLogic()