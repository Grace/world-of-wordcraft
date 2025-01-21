from dotenv import load_dotenv
from .modules.room_generator import RoomGenerator
from .modules.action_handler import ActionHandler
from .modules.game_state import GameState
import os

load_dotenv()

class GameLogic:
    def __init__(self, connected_clients):
        self.room_generator = RoomGenerator(os.getenv('OPENAI_API_KEY'))
        self.action_handler = ActionHandler(connected_clients)
        self.game_state = GameState()

    def handle_action(self, player, action):
        """Handle a player's action and return the result."""
        location = player["location"]
        room = self.game_state.get_room(location)
        
        if not room:
            room = self.room_generator.generate_room(location)
            self.game_state.save_room(location, room)

        return self.action_handler.handle(player, action, room)