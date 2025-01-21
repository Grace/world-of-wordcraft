from app.database import get_room, save_room

class GameState:
    def __init__(self):
        self.active_rooms = {}
        self.active_players = {}

    def get_room(self, coordinates):
        if coordinates not in self.active_rooms:
            room = get_room(coordinates)
            if room:
                self.active_rooms[coordinates] = room
        return self.active_rooms.get(coordinates)

    def save_room(self, coordinates, room):
        self.active_rooms[coordinates] = room
        save_room(coordinates, room)

    def get_player(self, player_id):
        return self.active_players.get(player_id)

    def update_player(self, player_id, player_data):
        self.active_players[player_id] = player_data