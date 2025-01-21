-- Initial schema creation
CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE,
    name_original TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    location_x INTEGER DEFAULT 0,
    location_y INTEGER DEFAULT 0,
    location_z INTEGER DEFAULT 0,
    inventory TEXT DEFAULT '[]',
    role_id TEXT DEFAULT 'player' REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS rooms (
    coordinates TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    exits TEXT DEFAULT '{}',
    npcs TEXT DEFAULT '[]',
    items TEXT DEFAULT '[]',
    puzzles TEXT DEFAULT '[]'
);

-- Add roles table
CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    permissions TEXT NOT NULL  -- JSON array of allowed commands
);

-- Insert default roles
INSERT OR IGNORE INTO roles (id, name, permissions) VALUES
    ('player', 'Player', '["look", "go", "take", "inventory", "logout", "highcontrast", "fontsize", "interact", "use", "solve"]'),
    ('moderator', 'Moderator', '["look", "go", "take", "inventory", "logout", "highcontrast", "fontsize", "interact", "use", "solve", "kick", "mute", "ban", "edit_room"]'),
    ('admin', 'Admin', '["look", "go", "take", "inventory", "logout", "highcontrast", "fontsize", "interact", "use", "solve", "kick", "mute", "ban", "edit_room", "grant_role", "spawn_item", "teleport"]');

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_player_name ON players(name COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_room_coordinates ON rooms(coordinates);