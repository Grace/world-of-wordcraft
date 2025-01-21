-- Initial schema creation
CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE,
    name_original TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    location_x INTEGER DEFAULT 0,
    location_y INTEGER DEFAULT 0,
    location_z INTEGER DEFAULT 0,
    inventory TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS rooms (
    coordinates TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    exits TEXT DEFAULT '{}',
    npcs TEXT DEFAULT '[]',
    items TEXT DEFAULT '[]',
    puzzles TEXT DEFAULT '[]'
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_player_name ON players(name COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_room_coordinates ON rooms(coordinates);