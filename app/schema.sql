-- Initial schema creation
CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL COLLATE NOCASE UNIQUE,
    password_hash TEXT NOT NULL,
    location TEXT DEFAULT '0,0,0',
    inventory TEXT DEFAULT '[]',
    role_id TEXT DEFAULT 'player' REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
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
    ('moderator', 'Moderator', '["look", "go", "take", "inventory", "logout", "highcontrast", "fontsize", "interact", "use", "solve", "kick", "mute", "ban", "edit_room_description"]'),
    ('admin', 'Admin', '["look", "go", "take", "inventory", "logout", "highcontrast", "fontsize", "interact", "use", "solve", "kick", "mute", "ban", "edit_room_description", "grant_role", "spawn_item", "teleport"]');

-- Add banned players table
CREATE TABLE IF NOT EXISTS banned_players (
    player_id TEXT PRIMARY KEY REFERENCES players(id),
    banned_by TEXT NOT NULL REFERENCES players(id),
    reason TEXT,
    banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_player_name ON players(username COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_room_coordinates ON rooms(coordinates);