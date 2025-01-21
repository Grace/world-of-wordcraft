from dotenv import load_dotenv
import os
import openai
from app.database import get_room, save_room, get_players_in_room, update_player_location
import random

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Content pools
NPCS = [
    {"name": "Old Merchant", "role": "trader", "dialogue": "I sell potions and rare items."},
    {"name": "Lost Scholar", "role": "quest_giver", "dialogue": "I seek ancient texts in these halls..."},
    {"name": "Wandering Mage", "role": "teacher", "dialogue": "The arcane arts are not to be trifled with."},
    {"name": "Gruff Dwarf", "role": "smith", "dialogue": "Need something forged? I'm your dwarf."},
    {"name": "Mysterious Elf", "role": "guide", "dialogue": "The shadows hold many secrets..."}
]

ITEMS = [
    {"name": "Rusty Key", "description": "An old key covered in rust.", "type": "key"},
    {"name": "Health Potion", "description": "A red liquid that restores health.", "type": "consumable"},
    {"name": "Ancient Scroll", "description": "A weathered scroll with mysterious writing.", "type": "quest"},
    {"name": "Magic Gem", "description": "A glowing gem humming with power.", "type": "valuable"},
    {"name": "Broken Sword", "description": "A sword that has seen better days.", "type": "weapon"}
]

PUZZLES = [
    {"type": "riddle", "text": "Speak friend and enter", "solution": "friend"},
    {"type": "combination", "text": "Find the sequence: Red, Blue, Green", "solution": "RGB"},
    {"type": "lock", "text": "This chest requires a specific key", "solution": "Rusty Key"},
    {"type": "pattern", "text": "Press the tiles in order of the stars", "solution": "1234"},
    {"type": "magic", "text": "Channel the correct element to open", "solution": "fire"}
]

def generate_room_description(coordinates):
    """
    Generate a detailed room description using OpenAI's GPT model.

    Args:
        coordinates (tuple): The (x, y, z) coordinates of the room.

    Returns:
        dict: A dictionary containing the room's description, exits, puzzles, NPCs, and items.
    """
    prompt = f"""You are generating content for a text-based MMORPG (MUD). Create an immersive room at coordinates {coordinates}.

Required elements:
1. DESCRIPTION: Write a vivid, screen-reader friendly description (2-3 sentences). Use concrete, spatial language.

2. EXITS: Include 2-3 logical exits (north/south/east/west/up/down). Each exit must:
   - Match the room's description
   - Connect logically to adjacent rooms
   - Include brief exit descriptions that match the opposite exit description from the last room based on the last direction taken by the player if generating a new room

3. INTERACTIVITY:
   - One puzzle or challenge (e.g., locked door, riddle)
   - One collectable item with clear description
   - One NPC with distinct personality and brief dialogue

Format rules:
- Use clear, concise language
- Maintain consistent spatial references
- Avoid visual-only descriptions
- Include audio/tactile details
- Keep paragraphs short for screen readers

Example output structure:
Description: [Room description]
Exits: [Exit list with brief descriptions]
Interactive: [Puzzle/challenge]
Items: [Collectables]
NPCs: [Character with dialogue]

Ensure all elements are logically connected and support navigation."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a MUD game master creating accessible, interconnected game spaces."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        text = response['choices'][0]['message']['content'].strip()
        exits = {direction: None for direction in ["north", "south", "east", "west", "up", "down"] 
                if direction in text.lower()}

        # Random content generation
        room_npc = random.choice(NPCS) if random.random() < 0.7 else None
        room_items = random.sample(ITEMS, k=random.randint(0, 2))
        room_puzzle = random.choice(PUZZLES) if random.random() < 0.3 else None

        return {
            "description": text,
            "exits": exits,
            "puzzle": room_puzzle,
            "npc": [room_npc] if room_npc else [],
            "items": room_items
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
        "w": "west",
        "u": "up",
        "d": "down"
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

    elif action.startswith(("interact with ", "use ", "solve ")):
        # Handle interactions with puzzles and objects
        parts = action.split(" ", 2)
        command = parts[0]
        target = parts[-1].lower()
        
        # Get puzzle from room
        puzzle = room.get("puzzle")
        if not puzzle:
            return "There's nothing to interact with here."
            
        if command == "solve" and "riddle" in puzzle.lower():
            # Handle riddle solving
            if target in puzzle.lower():  # Simple check if answer is in riddle text
                room["puzzle"] = None  # Mark puzzle as solved
                save_room(location, room)
                return "You solved the riddle! The chest creaks open..."
            return "That's not the correct answer."
            
        if command == "use":
            # Check if player has the item
            player_items = [item["name"].lower() for item in player.get("inventory", [])]
            if target not in player_items:
                return f"You don't have a {target}."
                
            if "key" in target and "chest" in puzzle.lower():
                room["puzzle"] = None
                save_room(location, room)
                return "The key fits! The chest opens with a satisfying click."
                
        return f"You try to {command} {target} but nothing happens."

    return "Invalid command. Try 'look', 'go <direction>', 'take <item>', 'talk to <npc>', or 'interact with <object>'."
