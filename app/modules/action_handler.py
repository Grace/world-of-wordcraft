from app.database import get_room, update_player_location, get_players_in_room

class ActionHandler:
    def __init__(self):
        self.direction_mapping = {
            "n": "north", "s": "south", "e": "east", "w": "west",
            "u": "up", "d": "down"
        }

    def handle(self, player, action, room):
        if action in self.direction_mapping:
            action = f"go {self.direction_mapping[action]}"

        if action.startswith("go "):
            return self._handle_movement(player, action, room)
        elif action in ["look", "l"]:
            return self._handle_look(player, room)
        elif action.startswith("take "):
            return self._handle_take(player, action, room)
        elif action.startswith(("interact ", "use ", "solve ")):
            return self._handle_interaction(player, action, room)
        
        return "Invalid command."

    def _handle_movement(self, player, action, room):
        direction = action.split(" ", 1)[1]
        if direction in room["exits"]:
            x, y, z = player["location"]
            if direction == "north": y += 1
            elif direction == "south": y -= 1
            elif direction == "east": x += 1
            elif direction == "west": x -= 1
            elif direction == "up": z += 1
            elif direction == "down": z -= 1
            
            player["location"] = (x, y, z)
            update_player_location(player["id"], (x, y, z))
            return f"You move {direction}."
        
        return f"You cannot go {direction}."

    def _handle_look(self, player, room):
        # Get players in room excluding current player
        players = get_players_in_room(player["location"], exclude=player["id"])
        
        # Format player list if any others present
        other_players = f"\nOther players here: {', '.join(players)}" if players else ""
        
        # Format NPC and item lists
        npcs = "\nNPCs: " + (", ".join([npc["name"] for npc in room.get("npcs", [])]) or "none")
        items = "\nItems: " + (", ".join([item["name"] for item in room.get("items", [])]) or "none")
        
        return f"{room['description']}{other_players}{npcs}{items}"

    def _handle_take(self, player, action, room):
        item_name = action.split(" ", 1)[1].lower()
        for item in room.get("items", []):
            if item["name"].lower() == item_name:
                room["items"].remove(item)
                player.setdefault("inventory", []).append(item)
                return f"You take the {item['name']}."
        return f"There is no {item_name} here."

    def _handle_interaction(self, player, action, room):
        parts = action.split(" ", 2)
        command = parts[0]
        target = parts[-1].lower()

        puzzles = room.get("puzzles")
        if len(puzzles)==0:
            return "There's nothing to interact with here."
        else:
            for puzzle in puzzles:
                if command == "solve" and puzzle["type"] == "riddle":
                    if target == puzzle["solution"].lower():
                        room["puzzle"] = None
                        return "You solved the riddle!"
                    return "That's not the correct answer."

        return f"You try to {command} {target} but nothing happens."