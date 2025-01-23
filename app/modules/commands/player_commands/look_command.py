class LookCommand(PlayerCommand):
        def __init__(self):
            super().__init__(name="look", description="Look around the room", required_roles=None)

def execute(self, player, room):
        # Get players in room excluding current player
        players = get_players_in_room(player["location"], exclude=player["id"])
        
        # Format player list if any others present
        other_players = f"\nOther players here: {', '.join(players)}" if players else ""
        
        # Format NPC and item lists
        npcs = "\nNPCs: " + (", ".join([npc["name"] for npc in room.get("npcs", [])]) or "none")
        items = "\nItems: " + (", ".join([item["name"] for item in room.get("items", [])]) or "none")