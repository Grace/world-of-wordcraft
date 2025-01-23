from typing import Dict, Any, Set, Optional
import logging
from ..commands.roles import Role

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, client_id: str, username: str) -> None:
        """Create new session for client with Player role"""
        self.sessions[client_id] = {
            'username': username,
            'roles': {Role.PLAYER},
            'logged_in': True
        }
        logger.info(f"Session created for client {client_id}")

    def end_session(self, client_id: str) -> None:
        """End client session and cleanup"""
        if client_id in self.sessions:
            del self.sessions[client_id]
            logger.info(f"Session ended for client {client_id}")

    def get_session(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get session data for client"""
        return self.sessions.get(client_id)

    def is_logged_in(self, client_id: str) -> bool:
        """Check if client is logged in"""
        return client_id in self.sessions

    def has_role(self, client_id: str, role: Role) -> bool:
        """Check if client has specific role"""
        if client_id not in self.sessions:
            return False
        return role in self.sessions[client_id]['roles']