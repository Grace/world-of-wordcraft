from app.database import check_permission, save_room, update_player_location, get_room, get_players_in_room, load_player

class ActionHandler:
    def __init__(self, connected_clients=None):
        self.connected_clients = connected_clients
        self.direction_mapping = {
            "n": "north", "s": "south", "e": "east", "w": "west",
            "u": "up", "d": "down",
            "north": "north", "south": "south", "east": "east", "west": "west",
            "up": "up", "down": "down"
        }
        self.admin_commands = {
            "grant_role": self._handle_grant_role,
            "spawn_item": self._handle_spawn_item,
            "teleport": self._handle_teleport
        }
        self.mod_commands = {
            "kick": self._handle_kick,
            "mute": self._handle_mute,
            "ban": self._handle_ban,
            "edit": self._handle_edit_room
        }

    def handle(self, player, action, room):
        command = action.split()[0].lower()
        
        # Check admin commands
        if command in self.admin_commands:
            if check_permission(player["id"], command):
                return self.admin_commands[command](player, action, room)
            return "You don't have permission to use that command."
            
        # Check mod commands
        if command in self.mod_commands:
            if check_permission(player["id"], command):
                return self.mod_commands[command](player, action, room)
            return "You don't have permission to use that command."
            
        # Handle regular commands
        if action.startswith("highcontrast "):
            return self._handle_highcontrast(action)
        elif action == "logout":
            return self._handle_logout(player)
        elif action in ["inventory", "i"]:
            return self._handle_inventory(player)
        elif action in self.direction_mapping:
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
        # Get full direction name from mapping
        raw_direction = action.split(" ", 1)[1]
        direction = self.direction_mapping.get(raw_direction.lower())
        
        if direction and direction in room["exits"]:
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
        
        return f"You cannot go {raw_direction}."

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

    def _handle_logout(self, player):
        """Handle player logout."""
        try:
            return {
                "type": "logout", 
                "message": f"Goodbye, {player['name_original']}! Come back soon."
            }
        except KeyError:
            return {
                "type": "error",
                "message": "Error during logout. Please try again."
            }

    def _handle_highcontrast(self, action):
        """Handle high contrast theme toggle."""
        setting = action.split(" ")[1].lower()
        if setting not in ["on", "off"]:
            return "Usage: highcontrast on|off"
            
        return {
            "type": "theme",
            "theme": "high-contrast" if setting == "on" else "default",
            "message": f"High contrast mode turned {setting}."
        }

    def _handle_inventory(self, player):
        """Display player's inventory."""
        items = player.get("inventory", [])
        if not items:
            return "Your inventory is empty."
            
        item_list = [item["name"] for item in items]
        return f"Your inventory contains:\n{', '.join(item_list)}"

    def _handle_grant_role(self, player, action, room):
        """Grant role to player (admin only)."""
        parts = action.split()
        if len(parts) != 3:
            return "Usage: grant_role <player_name> <role>"
            
        target_name = parts[1]
        role = parts[2]
        
        # Implementation details...
        return f"Granted {role} role to {target_name}"

    def _handle_edit_room(self, player, action, room):
        """Edit room description (mod+ only)."""
        parts = action.split(" ", 1)
        if len(parts) != 2:
            return "Usage: edit <new description>"
            
        room["description"] = parts[1]
        save_room(player["location"], room)
        return "Room description updated"

    def _handle_spawn_item(self, player, action, room):
        """Spawn an item in the current room (admin only)."""
        parts = action.split()
        if len(parts) < 2:
            return "Usage: spawn_item <item_name>"
            
        item_name = " ".join(parts[1:])
        new_item = {"name": item_name}
        
        room_items = room.get("items", [])
        room_items.append(new_item)
        room["items"] = room_items
        
        return f"Spawned {item_name} in the room."
        
    def _handle_teleport(self, player, action, room):
        """Teleport to specific coordinates (admin only)."""
        parts = action.split()
        if len(parts) != 4:
            return "Usage: teleport <x> <y> <z>"
            
        try:
            x, y, z = map(int, parts[1:4])
            player["location"] = (x, y, z)
            return f"Teleported to coordinates ({x}, {y}, {z})"
        except ValueError:
            return "Invalid coordinates. Use numbers only."
            
    def _handle_kick(self, player, action, room):
        """Kick a player (mod+ only)."""
        parts = action.split()
        if len(parts) < 2:
            return "Usage: kick <player_name>"
            
        target_name = parts[1].lower()
        
        # Find target player
        for player_id, websocket in self.connected_clients.items():
            target = load_player(player_id)
            if target and target["name"].lower() == target_name:
                return {
                    "type": "kick",
                    "target_id": player_id,
                    "message": f"Player {target['name_original']} has been kicked by {player['name_original']}"
                }
                    
        return f"Player {parts[1]} not found or not online."
        
    def _handle_mute(self, player, action, room):
        """Mute a player (mod+ only)."""
        parts = action.split()
        if len(parts) < 2:
            return "Usage: mute <player_name>"
        return f"Muted player {parts[1]}"
        
    def _handle_ban(self, player, action, room):
        """Ban a player (mod+ only)."""
        parts = action.split()
        if len(parts) < 2:
            return "Usage: ban <player_name>"
        return f"Banned player {parts[1]}"