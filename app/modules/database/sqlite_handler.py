import aiosqlite
import bcrypt
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SQLiteHandler:
    def __init__(self, db_path="game.db"):
        self.db_path = Path(db_path)
        self.init_db()

    def init_db(self):
        # Sync initialization
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            conn.close()

    async def create_player(self, username: str, password: str) -> tuple[bool, str]:
        async with aiosqlite.connect(self.db_path) as db:
            try:
                # Check if username exists
                async with db.execute(
                    "SELECT username FROM players WHERE username = ?", 
                    (username,)
                ) as cursor:
                    if await cursor.fetchone():
                        return False, "Username already exists"

                # Hash password
                password_hash = bcrypt.hashpw(
                    password.encode(), 
                    bcrypt.gensalt()
                ).decode()

                # Insert new player
                await db.execute(
                    """INSERT INTO players (username, password_hash) 
                    VALUES (?, ?)""", 
                    (username, password_hash)
                )
                await db.commit()
                return True, "Account created successfully"

            except Exception as e:
                logger.error(f"Database error: {e}")
                return False, "Error creating account"

    async def verify_login(self, username: str, password: str) -> tuple[bool, str]:
        async with aiosqlite.connect(self.db_path) as db:
            try:
                # Get player record
                async with db.execute(
                    "SELECT password_hash FROM players WHERE username = ?", 
                    (username,)
                ) as cursor:
                    record = await cursor.fetchone()
                    
                    if not record:
                        return False, "Player not found"
                    
                    stored_hash = record[0]
                    
                    # Verify password
                    if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                        # Update last login
                        await db.execute(
                            "UPDATE players SET last_login = CURRENT_TIMESTAMP WHERE username = ?",
                            (username,)
                        )
                        await db.commit()
                        return True, f"Welcome back, {username}!"
                    else:
                        return False, "Incorrect password"
                        
            except Exception as e:
                logger.error(f"Database error during login: {e}")
                return False, "Error during login"