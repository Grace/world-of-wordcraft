import random
import openai
from .content_pools import NPCS, ITEMS, PUZZLES
from app.database import save_room

class RoomGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key
        self.prompt_template = """You are generating content for a text-based MMORPG (MUD). Create an immersive room at coordinates {coordinates}.
        
        Required elements:
        1. DESCRIPTION: Write a vivid, screen-reader friendly description (2-3 sentences).
        2. EXITS: Include 2-3 logical exits (north/south/east/west/up/down).
        3. INTERACTIVITY: One puzzle or challenge.
        """

    def generate_room(self, coordinates, previous_room=None):
        try:
            description = self._get_gpt_description(coordinates)
            room = {
                "description": description,
                "exits": self._parse_exits(description),
                "npcs": self._generate_npcs(),
                "items": self._generate_items(),
                "puzzles": self._generate_puzzle()
            }
            save_room(coordinates, room)
            return room
        except Exception as e:
            return self._generate_fallback_room()

    def _get_gpt_description(self, coordinates):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a MUD game master creating accessible game spaces."},
                {"role": "user", "content": self.prompt_template.format(coordinates=coordinates)}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()

    def _parse_exits(self, description):
        exits = {}
        directions = ["north", "south", "east", "west", "up", "down"]
        for direction in directions:
            if direction in description.lower():
                exits[direction] = True
        return exits

    def _generate_npcs(self):
        return [random.choice(NPCS)] if random.random() < 0.7 else []

    def _generate_items(self):
        return random.sample(ITEMS, k=random.randint(0, 2))

    def _generate_puzzle(self):
        return random.choice(PUZZLES) if random.random() < 0.3 else None

    def _generate_fallback_room(self):
        return {
            "description": "A plain room stretches before you. The walls are smooth and featureless.",
            "exits": {"north": True},
            "npcs": [],
            "items": [],
            "puzzles": []
        }