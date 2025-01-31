import re

from app.modules.generators.item import Item
from app.modules.generators.npc import NPC


class Room:
    def __init__(self, name: str, description: str):
        self._name = name
        self._coordinates = None
        self._description = description
        self._items = []
        self._npcs = []
        self._exits = {}

    def get_name(self):
        return self._name

    def set_name(self, name: str):
        self._name = name

    def get_description(self):
        return self._description

    def set_description(self, description: str):
        self._description = description

    def add_item(self, item):
        self._items.append(item)

    def remove_item(self, item):
        if item in self._items:
            self._items.remove(item)

    def add_npc(self, npc):
        self._npcs.append(npc)

    def remove_npc(self, npc):
        if npc in self._npcs:
            self._npcs.remove(npc)

    def get_coordinates(self):
        return self._coordinates

    def set_coordinates(self, coordinates: str):
        if not self._validate_coordinates_string(coordinates):
            raise ValueError("Invalid coordinates format")
        self._coordinates = coordinates

    def set_exit(self, direction: str, room):
        self._exits[direction] = room

    def get_exit(self, direction: str):
        return self._exits.get(direction)

    def __str__(self):
        return f"{self._name}: {self._description}\nItems: {', '.join([item.name for item in self._items])}\nExits: {', '.join(self._exits.keys())}"

    def _validate_coordinates_string(self, coordinates: str) -> bool:
        pattern = r'^\d+,\d+,\d+$'
        return bool(re.match(pattern, coordinates))

    def to_dict(self):
        return {
            "coordinates": self._coordinates,
            "description": self._description,
            "exits": self._exits,
            "npcs": [{"id": npc.id, "name": npc.name, "description": npc.description} for npc in self._npcs],
            "items": [{"id": item.id, "name": item.name, "description": item.description} for item in self._items]
        }

    @classmethod
    def from_dict(cls, data: dict):
        room = cls(name="", description=data["description"])
        room.set_coordinates(data["coordinates"])
        room._exits = data["exits"]
        room._npcs = [NPC(npc["id"], npc["name"], npc["description"]) for npc in data["npcs"]]
        room._items = [Item(item["id"], item["name"], item["description"]) for item in data["items"]]
        return room