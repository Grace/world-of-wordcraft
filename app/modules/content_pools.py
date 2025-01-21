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