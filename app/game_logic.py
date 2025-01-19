from dotenv import load_dotenv
import os
import openai
from app.database import get_room, save_room, get_players_in_room, update_player_location

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_room_description(coordinates):
    """
    Generate a detailed room description using OpenAI's GPT model.

    Args:
        coordinates (tuple): The (x, y, z) coordinates of the room.

    Returns:
        dict: A dictionary containing the room's description, exits, puzzles, NPCs, and items.
    """
    prompt = f"""
    You are building a text-based MMORPG. Generate a detailed description of a room located at coordinates {coordinates} (x, y, z).
    - Include 2-3 possible exits (north, south, east, west, up, down).
    - Add a puzzle or challenge that players can solve (e.g., a locked chest, a riddle).
    - Include 1-2 NPCs with brief descriptions and dialogue.
    - Place 1-2 items in the room that players can interact with or pick up.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # You can also use "gpt-3.5-turbo" for lower cost.
            messages=[
                {"role": "system", "content": "You are a room description generator for an MMORPG."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        # Access the response content correctly for ChatCompletion API
        text = response['choices'][0]['message']['content'].strip()
        # Extract exits based on common directions
        exits = {direction: None for direction in ["north", "south", "east", "west", "up", "down"] if direction in text.lower()}
        return {
            "description": text,
            "exits": exits,
            "puzzle": "Solve the riddle to open the chest.",
            "npc": [{"name": "Old Merchant", "dialogue": "I sell potions and rare items."}],
            "items": [{"name": "Mysterious Key", "description": "A key that unlocks something important."}]
        }
    except Exception as e:
        print(f"Error generating room description: {e}")
        return {
            "description": "This room is featureless and unremarkable.",
            "exits": {},
            "puzzle": None,
            "npc": [],
            "items": []
        }

def handle_action(player, action):
    """
    Handle player actions such as movement, interacting with NPCs, and solving puzzles.
    
    Args:
        player (dict): The player's current state, including location and inventory.
        action (str): The player's input command.

    Returns:
        str: The result or response to the player's action.
    """
    location = player["location"]

    # Map abbreviations to full directions
    direction_mapping = {
        "n": "north",
        "s": "south",
        "e": "east",
        "w": "west"
    }

    # Convert abbreviations to full commands
    if action in direction_mapping:
        action = f"go {direction_mapping[action]}"

    # Generate or retrieve the current room
    room = get_room(location)
    if not room:
        room = generate_room_description(location)
        save_room(location, room)

    if action == "look" or action == "l":
        # Show room description, NPCs, and items
        players_in_room = get_players_in_room(location, exclude=player["id"])
        other_players = f"Other players here: {', '.join(players_in_room)}" if players_in_room else "You are alone in this room."
        npc_text = ", ".join([npc["name"] for npc in room.get("npc", [])])
        item_text = ", ".join([item["name"] for item in room.get("items", [])])
        return f"{room['description']}\nNPCs: {npc_text}\nItems: {item_text}\n{other_players}"

    elif action.startswith("go "):
        # Movement logic
        direction = action.split(" ", 1)[1]
        if direction in room["exits"]:
            # Calculate new coordinates based on direction
            x, y, z = location
            if direction == "north":
                y += 1
            elif direction == "south":
                y -= 1
            elif direction == "east":
                x += 1
            elif direction == "west":
                x -= 1
            elif direction == "up":
                z += 1
            elif direction == "down":
                z -= 1

            new_location = (x, y, z)
            player["location"] = new_location
            update_player_location(player["id"], new_location)
            return f"You move {direction}. {handle_action(player, 'look')}"
        return "You can't go that way."

    elif action.startswith("take "):
        # Picking up items
        item_name = action.split(" ", 1)[1]
        item = next((item for item in room.get("items", []) if item["name"].lower() == item_name.lower()), None)
        if item:
            player["inventory"].append(item)
            room["items"].remove(item)
            save_room(location, room)
            return f"You picked up {item['name']}."
        return f"There is no {item_name} here."

    elif action.startswith("talk to "):
        # Talking to NPCs
        npc_name = action.split(" ", 2)[-1]
        npc = next((npc for npc in room.get("npc", []) if npc["name"].lower() == npc_name.lower()), None)
        if npc:
            return f"{npc['name']} says: {npc['dialogue']}"
        return f"There is no {npc_name} here."

    elif action == "inventory":
        # Display inventory
        inventory_list = ", ".join([item["name"] for item in player.get("inventory", [])])
        return f"Your inventory: {inventory_list}" if inventory_list else "Your inventory is empty."

    return "Invalid command. Try 'look', 'go <direction>', 'take <item>', or 'talk to <npc>'."
