class RoomGenerator:
    STARTING_ROOM = {
        "coordinates": "0,0,0",
        "description": "You find yourself in a cozy stone chamber lit by glowing crystals. A friendly tutorial guide stands nearby ready to help. On the wall, you see glowing signs explaining basic commands like 'look' and 'help'.",
        "exits": {
            "north": "0,1,0",
            "east": "1,0,0", 
            "west": "-1,0,0"
        },
        "npcs": [
            {
                "id": "tutorial_guide",
                "name": "Tutorial Guide",
                "description": "A friendly NPC ready to help new players get started."
            }
        ],
        "items": [
            {
                "id": "welcome_scroll",
                "name": "Welcome Scroll",
                "description": "A scroll containing basic game commands and tips."
            }
        ]
    }

    def get_starting_room(self):
        """Returns the default starting room"""
        return self.STARTING_ROOM.copy()

    def generate_room(self, coordinates, previous_room=None):
        if coordinates == self.STARTING_ROOM["coordinates"]:
            return self.STARTING_ROOM