import bcrypt
import logging
import re
from typing import Tuple
from .db_connection import DatabaseConnection
from ..generators.room import Room
from ..generators.room_generator import RoomGenerator

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.room_generator = RoomGenerator()

    async def create_user(self, username: str, password: str) -> Tuple[bool, str]:
        if not self._validate_username(username):
            return False, "Invalid username format"
        try:
            # Hash password and store as bytes
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode(), salt)
            async with self.db.connect() as conn:
                await conn.execute(
                    "INSERT INTO players (username, password_hash) VALUES (?, ?)",
                    (username, hashed)
                )
                await conn.commit()
                self.log_starting_room()
                return True, "User created successfully"
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False, "Username already exists"

    def log_starting_room(self):
        starting_room = Room.from_dict(self.room_generator.get_starting_room())
        print(starting_room.get_description())

    async def verify_user(self, username: str, password: str) -> Tuple[bool, str]:
        try:
            async with self.db.connect() as conn:
                cursor = await conn.execute(
                    "SELECT password_hash FROM players WHERE username = ?",
                    (username,)
                )
                row = await cursor.fetchone()
            
            if not row:
                return False, "Invalid username or password"

            stored_hash = row[0]
            if bcrypt.checkpw(password.encode(), stored_hash):
                return True, "Login successful"
            return False, "Invalid username or password"
            
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return False, "Authentication failed"

    def _validate_username(self, username: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9_]{3,20}$', username))